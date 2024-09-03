# Scraper

MAX_TRIES = 5
MAX_TIME = 60

MAX_TRIES_DB_REQUESTS = 10


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
            "filename": 'log/scraper.log'
        },
        "scraper":
        {
            "formatter": "simple",
            "class": 'logging.StreamHandler',
            "level": "INFO",
        },
    },
    "loggers":
    {
        "scraper": {"handlers": ["scraper", "scraper_file"], "level": "DEBUG", "propagate": False},
    }
}
