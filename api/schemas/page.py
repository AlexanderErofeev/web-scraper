from pydantic import BaseModel, ConfigDict, Field


class SPageBase(BaseModel):
    title: str | None = Field(title='Заголовок страницы', examples=['Экскурсии в Таиланде'])
    url: str = Field(title='Адрес страницы', examples=['https://anextour.ru/excursions/thailand'])

    model_config = ConfigDict(from_attributes=True)


class SPageList(SPageBase):
    id: int = Field(title='ID страницы', examples=[4974])


class SPageDetail(SPageList):
    html: str | None = Field(title='Полный HTML страницы', examples=["<!DOCTYPE html><html> ... </html>"])


class SPageAdd(SPageBase):
    html: str | None = Field(title='Полный HTML страницы', examples=["<!DOCTYPE html><html> ... </html>"])
