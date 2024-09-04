from sqlalchemy import select, func, text
from ..models.page import Page
from ..schemas.page import SPageList, SPageDetail, SPageAdd
from ..database import SessionLocal


class PageRepository:
    @classmethod
    async def add_task(cls, task: SPageAdd) -> int:
        async with SessionLocal() as session:
            data = task.model_dump()
            new_task = Page(**data)
            session.add(new_task)
            await session.flush()
            await session.commit()
            return new_task.id

    @classmethod
    async def get_pages(cls, q: str = None) -> list[SPageList]:
        async with SessionLocal() as session:
            await session.execute(text('CREATE EXTENSION IF NOT EXISTS pg_trgm'))

            if q is None:
                query = select(Page).limit(100)
            else:
                columns = func.coalesce(Page.title, '').concat(func.coalesce(Page.url, ''))
                columns = columns.self_group()

                query = select(
                    Page,
                ).where(
                    func.similarity(columns, q) > 0.05
                    # Page.title.bool_op('%')(q),
                ).order_by(
                    func.similarity(columns, q).desc(),
                ).limit(100)

            result = await session.execute(query)
            task_models = result.scalars().all()
            tasks = [SPageList.model_validate(task_model) for task_model in task_models]
            return tasks

    @classmethod
    async def get_page(cls, id: int) -> SPageDetail | None:
        async with SessionLocal() as session:
            query = select(Page).where(id == Page.id)
            result = await session.execute(query)
            task_model = result.scalars().one_or_none()
            if task_model is not None:
                task = SPageDetail.model_validate(task_model)
                return task
            return None
