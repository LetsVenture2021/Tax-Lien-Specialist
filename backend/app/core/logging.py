"""Central logging configuration for structured application logs."""

import logging
import logging.config
import sys
from typing import Any

import structlog

from app.core.config import settings


def configure_logging(force: bool = False) -> None:
    """Initialise structlog + standard logging handlers if not already configured."""
    if getattr(configure_logging, "_configured", False) and not force:
        return

    logging_config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "plain": {
                "format": "%(message)s",
            },
        },
        "handlers": {
            "default": {
                "level": settings.LOG_LEVEL,
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "plain",
            }
        },
        "root": {
            "handlers": ["default"],
            "level": settings.LOG_LEVEL,
        },
    }

    logging.config.dictConfig(logging_config)

    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer() if settings.LOG_FORMAT == "json" else structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(settings.LOG_LEVEL)),
        cache_logger_on_first_use=True,
    )

    configure_logging._configured = True
