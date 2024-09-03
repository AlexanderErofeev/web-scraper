from pydantic import BaseModel, ConfigDict


class SPageList(BaseModel):
    id: int
    title: str
    url: str

    model_config = ConfigDict(from_attributes=True)


class SPageDetail(SPageList):
    html: str


class SPageAdd(BaseModel):
    title: str | None
    url: str
    html: str | None
