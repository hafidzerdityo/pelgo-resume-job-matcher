import logging
import sys

import structlog


def setup_logging(log_level: int = logging.INFO) -> None:
    """Configures structured logging for the application and backend workers."""
    
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )
    
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Returns a structlog logger instance."""
    return structlog.get_logger(name)

from contextlib import contextmanager
import time
from typing import Generator

@contextmanager
def log_flow(logger: structlog.BoundLogger, layer: str, function: str, **fields) -> Generator[None, None, None]:
    """Mimics vb-backend's LogFlow for tracing start/end durations."""
    start_time = time.time()
    logger.info(f"[START: {layer} {function}]", **fields)
    try:
        yield
        duration = int((time.time() - start_time) * 1000)
        logger.info(f"[END: {layer} {function} (SUCCESS)]", duration_ms=duration, **fields)
    except Exception as e:
        duration = int((time.time() - start_time) * 1000)
        logger.error(f"[END: {layer} {function} (FAILED)]", duration_ms=duration, error=str(e), **fields)
        raise e
