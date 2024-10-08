import asyncio
import os
from time import time
from typing import Set, List
from urllib.parse import urlparse, ParseResult
import aiohttp
import aiofiles as aiof
from bs4 import BeautifulSoup
import backoff
from .repositories.pages import PageRepository
from app.schemas.page import SPageAdd
from .config import LOG_CONFIG
import logging.config
from uuid import uuid4
from pathlib import Path
import argparse
from .dependencies import get_scraper_settings


scraper_settings = get_scraper_settings()
logging.config.dictConfig(LOG_CONFIG)
log = logging.getLogger('scraper')

visited_urls = set
domain = str
sem = asyncio.Semaphore
sem_db = asyncio.Semaphore


@backoff.on_exception(backoff.expo,
                      aiohttp.ClientError,
                      max_tries=scraper_settings.max_request_attempts,
                      max_time=scraper_settings.timeout_for_page)
async def execute_request(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=scraper_settings.timeout_request, raise_for_status=True) as resp:
            return await resp.text()


async def get_html(url: str) -> str | None:
    try:
        html = await execute_request(url)
        return html
    except Exception as err:
        log.warning(f'Failed to get html from {url}: {err.__class__.__name__}')
        return None


def is_internal_link(link: ParseResult) -> bool:
    if link.path in ('', '/'):
        return False
    if link.scheme == '' and link.netloc == '':
        return True
    if link.scheme not in ('http', 'https'):
        return False
    return link.netloc == domain


def format_link(link: ParseResult) -> str:
    return (link._replace(
        scheme='https',
        netloc=domain,
        fragment='')
            .geturl())


def get_internal_links(page: str) -> Set[str]:
    page = BeautifulSoup(page, 'html.parser')
    link_tags = page.body.find_all('a') if page and page.body else []

    page_links = []
    for tag in link_tags:
        link = urlparse(tag.get('href'))
        if not is_internal_link(link):
            continue
        link = format_link(link)
        page_links.append(link)

    return set(page_links)


def get_title(page: str) -> str:
    page = BeautifulSoup(page, 'html.parser')
    title = page.body.find('h1') if page and page.body else None
    return title.text if title else None


async def save_page(page: str, url: str) -> None:
    page_title = get_title(page)
    file_name = f"{uuid4()}.html"
    async with aiof.open(Path('app/scraper_htmls', file_name), "w", encoding='utf-8') as out:
        await out.write(page)
        await out.flush()
    page_obj = SPageAdd(title=page_title, url=url, html=file_name)
    async with sem_db:
        await PageRepository.add_page(page_obj)


async def parse_site(
        host: str,
        max_depth: int,
        parallel_request_count: int
) -> None:
    global visited_urls
    global domain
    global sem
    global sem_db

    visited_urls = set()
    domain = host
    sem = asyncio.Semaphore(parallel_request_count)
    sem_db = asyncio.Semaphore(scraper_settings.max_requests_to_db)

    url = f'https://{host}'

    log.info(f'Parsing site: {host} started')
    start_time = time()
    await parse_site_recursive(url, max_depth)
    total_time = int(time() - start_time)
    log.info(f'Parsing site: {host} finished, pages: {len(visited_urls)}, total time: {total_time} sec.')


async def processing_page(url: str, max_depth: int) -> Set[str]:
    global visited_urls

    async with sem:
        page = await get_html(url)

    if page is None:
        return set()

    log.debug(f'Parsing page: {url} started')

    await save_page(page, url)

    if max_depth == 1:
        log.debug(f'Parsing page: {url} finished, max depth reached')
        return set()

    page_links = get_internal_links(page)
    new_page_links = page_links - visited_urls

    log.debug(f'Parsing page: {url} finished, links: {len(page_links)}, new links: {len(new_page_links)}')

    visited_urls = visited_urls | new_page_links

    return new_page_links


async def parse_site_recursive(url: str, max_depth: int) -> None:
    new_links = await processing_page(url, max_depth)

    tasks = []
    for link in new_links:
        task = asyncio.create_task(parse_site_recursive(link, max_depth - 1))
        tasks.append(task)
    del new_links
    await asyncio.gather(*tasks)


async def main():
    os.makedirs('app/scraper_htmls', exist_ok=True)
    parser = argparse.ArgumentParser(description="Парсер")
    parser.add_argument("--host", type=str, help="host сайта для парсинга", required=True)
    parser.add_argument("--max_depth", type=int, help="Глубина парсинга", required=True)
    parser.add_argument("--request_count", type=int, help="Максимум одновременных запросов", required=True)
    args = parser.parse_args()
    await parse_site(args.host, args.max_depth, args.request_count)


asyncio.run(main())
