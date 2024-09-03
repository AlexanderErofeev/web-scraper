from sqlalchemy import select
from ..models.page import Page
from ..schemas.page import SPageList, SPageDetail
from ..database import SessionLocal


class PageRepository:
    @classmethod
    async def get_pages(cls) -> list[SPageList]:
        async with SessionLocal() as session:
            query = select(Page)
            result = await session.execute(query)
            task_models = result.scalars().all()
            tasks = [SPageList.model_validate(task_model) for task_model in task_models]
            return tasks

    @classmethod
    async def get_page(cls, id: int) -> SPageDetail | None:
        async with SessionLocal() as session:
            query = select(Page).where(id == Page.id)
            result = await session.execute(query)
            a = Page()
            task_model = result.scalars().one_or_none()
            if task_model is not None:
                task = SPageDetail.model_validate(task_model)
                return task
            return None
