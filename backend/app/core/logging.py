import logging
from logging.config import dictConfig

from .config import get_settings

settings = get_settings()


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(levelname)s %(asctime)s [%(name)s] %(message)s",
        }
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        }
    },
    "root": {
        "level": settings.LOG_LEVEL,
        "handlers": ["default"],
    },
}


def setup_logging() -> None:
    dictConfig(LOGGING_CONFIG)
    logging.getLogger(__name__).debug("Logging initialized with level %s", settings.LOG_LEVEL)
