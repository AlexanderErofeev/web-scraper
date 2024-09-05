from pathlib import Path
from fastapi import APIRouter, HTTPException
from ..schemas.page import SPageList, SPageDetail
from ..repositories.pages import PageRepository
import aiofiles as aiof


router = APIRouter(prefix="/pages")


@router.get("/", response_model=list[SPageList])
async def get_pages(q: str = None):
    pages = await PageRepository.get_pages(q)
    return pages


@router.get("/{id}", response_model=SPageDetail)
async def get_page(id: int):
    page = await PageRepository.get_page(id)

    if page is None:
        raise HTTPException(
            status_code=404,
            detail="Page not found"
        )

    file = Path('app/scraper_htmls', page.html)
    async with aiof.open(file, mode='r', encoding='utf-8') as f:
        contents = await f.read()
        page.html = contents

    return page
