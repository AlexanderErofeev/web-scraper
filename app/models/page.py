from sqlalchemy import Index, func
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Model


class Page(Model):
    __tablename__ = "pages"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str | None]
    url: Mapped[str]
    html: Mapped[str | None]

    # __table_args__ = (
    #     Index(
    #         'page_title_url_trgm_idx',
    #
    #         func.coalesce('title', '').concat(func.coalesce('url', '')).label('columns'),
    #
    #         postgresql_using='gin',
    #         postgresql_ops={
    #             'columns': 'gin_trgm_ops',
    #         },
    #     ),
    # )
