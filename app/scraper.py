import asyncio
import os
from time import time
from typing import Set, List
from urllib.parse import urlparse, ParseResult
import aiohttp
import aiofiles as aiof
from bs4 import BeautifulSoup
import backoff
from api.repositories.pages import PageRepository
from api.schemas.page import SPageAdd
from api.config import LOG_CONFIG
import logging.config
from playwright.async_api import async_playwright
from uuid import uuid4
from pathlib import Path
import argparse
from api.dependencies import get_scraper_settings


scraper_settings = get_scraper_settings()
logging.config.dictConfig(LOG_CONFIG)
visited_urls = set()
log = logging.getLogger('scraper')


@backoff.on_exception(backoff.expo,
                      aiohttp.ClientError,
                      max_tries=scraper_settings.max_request_attempts,
                      max_time=scraper_settings.max_time_for_page)
async def get_html(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.text()


async def get_html_js(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        html = await page.content()
        await browser.close()
        return html


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
    file_name = f"{uuid4()}.html"
    async with aiof.open(Path('app/scraper_htmls', file_name), "w", encoding='utf-8') as out:
        await out.write(page)
        await out.flush()
    page_obj = SPageAdd(title=page_title, url=url, html=file_name)
    await PageRepository.add_task(page_obj)


async def parse_site(
        host: str,
        max_depth: int,
        parallel_request_count: int
) -> None:
    url = f'https://{host}'
    sem = asyncio.Semaphore(parallel_request_count)
    sem_db = asyncio.Semaphore(scraper_settings.max_requests_to_db)

    log.info(f'Parsing site: {host} started')
    t1 = time()
    await parse_site_recursive(url, max_depth, host, sem, sem_db)
    log.info(f'Parsing site: {host} finished, pages: {len(visited_urls)}, total time: {time() - t1}')


async def parocessing_gage(url, max_depth, domain, sem, sem_db) -> List[str]:
    global visited_urls

    async with sem:
        page = await get_html(url)

    log.debug(f'Parsing page: {url} started')

    async with sem_db:
        await save_page_to_db(page, url)

    if max_depth == 1:
        log.debug(f'Parsing page: {url} finished, max depth reached')
        return []

    page_links = get_internal_links(page, domain)
    new_page_links = page_links - visited_urls

    log.debug(f'Parsing page: {url} finished, links: {len(page_links)}, new links: {len(new_page_links)}')

    visited_urls = visited_urls | new_page_links

    return new_page_links


async def parse_site_recursive(
        url: str,
        max_depth: int,
        domain: str,
        sem: asyncio.Semaphore,
        sem_db: asyncio.Semaphore,
):
    new_links = await parocessing_gage(url, max_depth, domain, sem, sem_db)

    tasks = [asyncio.create_task(parse_site_recursive(link, max_depth - 1, domain, sem, sem_db)) for link in
             new_links]
    await asyncio.gather(*tasks)


async def main():
    os.makedirs('app/scraper_htmls', exist_ok=True)
    parser = argparse.ArgumentParser(description="Парсер")
    parser.add_argument("host", type=str, help="host сайта для прсинга")
    parser.add_argument("max_depth", type=int, help="Глубина парсинга")
    parser.add_argument("request_count", type=int, help="Максимум одновременных запросов")
    args = parser.parse_args()
    await parse_site(args.host, args.max_depth, args.request_count)


asyncio.run(main())
