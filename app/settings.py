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
    }
}
