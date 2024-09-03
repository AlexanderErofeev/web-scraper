from sqlalchemy.orm import Mapped, mapped_column
from ..database import Model


class Page(Model):
    __tablename__ = "pages"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str | None]
    url: Mapped[str]
    html: Mapped[str | None]
