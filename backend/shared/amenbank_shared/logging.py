import logging
import sys

import structlog


def setup_logging(service_name: str, log_level: str = "INFO") -> None:
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=log_level)
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, log_level, logging.INFO)),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )
    structlog.contextvars.bind_contextvars(service=service_name)


def get_logger(name: str):
    return structlog.get_logger(name)
