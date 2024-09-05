from pydantic_settings import BaseSettings


class DBSettings(BaseSettings):
    username: str
    password: str
    database: str
    host: str
    port: str

    class Config:
        env_prefix = "DB_"
        env_file = ".env"
        extra = "ignore"


class ScraperSettings(BaseSettings):
    max_request_attempts: int
    max_time_for_page: int
    max_requests_to_db: int

    class Config:
        env_prefix = "SCRAPER_"
        env_file = ".env"
        extra = "ignore"


LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        'simple': {
            'format': '[{asctime}] {levelname} {message}',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'style': '{',
        },
    },
    "handlers":
    {
        "scraper_file":
        {
            "formatter": "simple",
            "class": 'logging.FileHandler',
            "filename": 'app/log/scraper.log'
        },
        "uvicorn_default_file":
        {
            "formatter": "simple",
            "class": 'logging.FileHandler',
            "filename": 'app/log/uvicorn_default.log'
        },
        "uvicorn_access_file":
        {
            "formatter": "simple",
            "class": 'logging.FileHandler',
            "filename": 'app/log/uvicorn_access.log'
        },
        "scraper":
        {
            "formatter": "simple",
            "class": 'logging.StreamHandler',
            # "level": "INFO",
        },
    },
    "loggers":
    {
        "scraper": {"handlers": ["scraper", "scraper_file"], "level": "DEBUG", "propagate": False},
        "uvicorn": {"handlers": ["uvicorn_default_file"], "level": "INFO", "propagate": False},
        "uvicorn.access": {"handlers": ["uvicorn_access_file"], "level": "INFO", "propagate": False},
    }
}
