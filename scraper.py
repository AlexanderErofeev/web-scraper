import asyncio
from time import time
from typing import Set
from urllib.parse import urlparse, ParseResult
import aiohttp
from bs4 import BeautifulSoup
import backoff
from api.repositories.pages import PageRepository
from api.schemas.page import SPageAdd
from settings import MAX_TRIES, MAX_TIME, LOG_CONFIG, MAX_TRIES_DB_REQUESTS
import logging
import logging.config

logging.config.dictConfig(LOG_CONFIG)
visited_urls = set()


@backoff.on_exception(backoff.expo, aiohttp.ClientError, max_tries=MAX_TRIES, max_time=MAX_TIME)
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
    page = BeautifulSoup(page, 'html.parser')
    link_tegs = page.body.find_all('a') if page and page.body else []

    page_links = []
    for teg in link_tegs:
        link = urlparse(teg.get('href'))
        if not is_internal_link(link, domain):
            continue
        link = format_link(link, domain)
        page_links.append(link)

    return set(page_links)


def get_title(page: str) -> str:
    page = BeautifulSoup(page, 'html.parser')
    title = page.body.find('h1') if page and page.body else None
    return title.text if title else None


async def save_page_to_db(page: str, url: str) -> None:
    page_title = get_title(page)
    page_obj = SPageAdd(title=page_title, url=url, html='')
    await PageRepository.add_task(page_obj)


async def parse_site(
        url: str,
        max_depth: int,
        parallel_request_count: int
) -> None:
    domain = urlparse(url).netloc
    sem = asyncio.Semaphore(parallel_request_count)
    sem_db = asyncio.Semaphore(MAX_TRIES_DB_REQUESTS)
    log = logging.getLogger('scraper')

    log.info(f'Parsing site: {domain} started')
    t1 = time()
    await parse_site_recursive(url, max_depth, domain, sem, sem_db, log)
    log.info(f'Parsing site: {domain} finished, pages: {len(visited_urls)}, total time: {time() - t1}')


async def parse_site_recursive(
        url: str,
        max_depth: int,
        domain: str,
        sem: asyncio.Semaphore,
        sem_db: asyncio.Semaphore,
        log: logging.Logger,
):
    global visited_urls

    async with sem:
        page = await get_html(url)

    log.debug(f'Parsing page: {url} started')

    async with sem_db:
        await save_page_to_db(page, url)

    if max_depth == 1:
        log.debug(f'Parsing page: {url} finished, max depth reached')
        return

    page_links = get_internal_links(page, domain)
    new_page_links = page_links - visited_urls

    log.debug(f'Parsing page: {url} finished, links: {len(page_links)}, new links: {len(new_page_links)}')

    visited_urls = visited_urls | new_page_links

    tasks = [asyncio.create_task(parse_site_recursive(link, max_depth - 1, domain, sem, sem_db, log)) for link in
             new_page_links]
    await asyncio.gather(*tasks)


async def main():
    await parse_site('https://anextour.ru/', 3, 20)


asyncio.run(main())
