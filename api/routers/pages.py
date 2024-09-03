from fastapi import APIRouter, HTTPException
from ..schemas.page import SPageList, SPageDetail
from ..repositories.pages import PageRepository


router = APIRouter(prefix="/pages")


@router.get("/", response_model=list[SPageList])
async def get_tasks():
    pages = await PageRepository.get_pages()
    return pages


@router.get("/{page_id}", response_model=SPageDetail)
async def get_page(id: int):
    page = await PageRepository.get_page(id)

    if page is None:
        raise HTTPException(
            status_code=404,
            detail="Page not found"
        )

    return page
