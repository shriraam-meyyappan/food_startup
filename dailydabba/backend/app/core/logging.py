"""Console logging with UTC timestamps."""

import logging
import time
from logging.config import dictConfig


class UTCFormatter(logging.Formatter):
    """Format timestamps in UTC, independently of the host's timezone."""

    converter = time.gmtime


def configure_logging(level: str) -> None:
    """Send application and Uvicorn logs to one console handler."""
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": UTCFormatter,
                    "format": "%(asctime)sZ %(levelname)s %(name)s: %(message)s",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                }
            },
            "root": {"handlers": ["console"], "level": level},
            "loggers": {
                "uvicorn": {"handlers": [], "propagate": True},
                "uvicorn.error": {"handlers": [], "propagate": True},
                "uvicorn.access": {"handlers": [], "propagate": True},
            },
        }
    )
