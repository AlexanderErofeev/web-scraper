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
