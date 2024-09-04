from pydantic import BaseModel, ConfigDict, Field


class SPageBase(BaseModel):
    title: str | None = Field(examples=['Экскурсии в Таиланде'])
    url: str = Field(examples=['https://anextour.ru/excursions/thailand'])

    model_config = ConfigDict(from_attributes=True)


class SPageList(SPageBase):
    id: int = Field(examples=[4974])


class SPageDetail(SPageList):
    html: str | None = Field(examples=["<!DOCTYPE html><html> ... </html>"])


class SPageAdd(SPageBase):
    html: str | None = Field(examples=["<!DOCTYPE html><html> ... </html>"])
