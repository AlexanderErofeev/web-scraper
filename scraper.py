import asyncio
from time import time
from typing import Set
from urllib.parse import urlparse, ParseResult
import aiohttp
from bs4 import BeautifulSoup
import backoff


visited_urls = set()
test_urls = []


@backoff.on_exception(backoff.expo, aiohttp.ClientError, max_tries=5, max_time=60)
async def get_html(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.text()


def is_internal_link(link: ParseResult, domain: str) -> bool:
    if link.path in ('', '/'):
        return False
    if link.scheme == '' and link.netloc == '':
        return True
    if link.scheme not in ('http', 'https'):
        return False
    return link.netloc == domain


def format_link(link: ParseResult, domain: str) -> str:
    return (link._replace(
        scheme='https',
        netloc=domain,
        fragment='')
            .geturl())


def get_internal_links(page: str, domain: str) -> Set[str]:
    link_tegs = (BeautifulSoup(page, 'html.parser')
                 .body
                 .find_all('a'))

    page_links = []
    for teg in link_tegs:
        link = urlparse(teg.get('href'))
        if not is_internal_link(link, domain):
            continue
        link = format_link(link, domain)
        page_links.append(link)

    return set(page_links)


async def parse_site(
        url: str,
        max_depth: int,
        parallel_request_count: int
) -> None:
    domain = urlparse(url).netloc
    sem = asyncio.Semaphore(parallel_request_count)
    await parse_site_recursive(url, max_depth, domain, sem)


async def parse_site_recursive(
        url: str,
        max_depth: int,
        domain: str,
        sem: asyncio.Semaphore
):
    global visited_urls

    async with sem:
        page = await get_html(url)

    print(url)
    test_urls.append(url)

    if max_depth == 1:
        return

    page_links = get_internal_links(page, domain)
    new_page_links = page_links - visited_urls

    visited_urls = visited_urls | new_page_links

    tasks = [asyncio.create_task(parse_site_recursive(link, max_depth - 1, domain, sem)) for link in new_page_links]
    await asyncio.gather(*tasks)


async def main():
    t1 = time()
    await parse_site('https://anextour.ru/', 5, 20)

    print(len(visited_urls))
    print(time() - t1)


asyncio.run(main())
