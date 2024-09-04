from pydantic import BaseModel


class SPageBase(BaseModel):
    title: str | None
    url: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Экскурсии в Таиланде",
                "url": "https://anextour.ru/excursions/thailand",
            }
        }
    }


class SPageList(SPageBase):
    id: int

    model_config = {
        "json_schema_extra": {
            "example": {
                **SPageBase.model_config.get("json_schema_extra").get("example"),
                "id": 1873,
            }
        }
    }


class SPageDetail(SPageList):
    html: str | None

    model_config = {
        "json_schema_extra": {
            "example": {
                **SPageList.model_config.get("json_schema_extra").get("example"),
                "html": "<!DOCTYPE html><html> ... </html>",
            }
        }
    }


class SPageAdd(SPageBase):
    html: str | None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    **SPageBase.model_config.get("json_schema_extra").get("example"),
                    "html": "<!DOCTYPE html><html> ... </html>",
                }
            ]
        }
    }
