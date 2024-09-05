from functools import lru_cache
from sqlalchemy.orm import Session
from app import config, database


def get_db() -> Session:
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@lru_cache
def get_db_settings() -> config.DBSettings:
    return config.DBSettings()


@lru_cache
def get_scraper_settings() -> config.ScraperSettings:
    return config.ScraperSettings()
