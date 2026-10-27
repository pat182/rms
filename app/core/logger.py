import json
import logging
from typing import Any


logger = logging.getLogger("rms")


def log_info(message: str, data: Any = None) -> None:
    _log(logging.INFO, message, data)


def log_warning(message: str, data: Any = None) -> None:
    _log(logging.WARNING, message, data)


def log_error(message: str, data: Any = None) -> None:
    _log(logging.ERROR, message, data)


def log_debug(message: str, data: Any = None) -> None:
    _log(logging.DEBUG, message, data)


def _log(level: int, message: str, data: Any = None) -> None:
    if data is None:
        logger.log(level, message)
        return

    try:
        formatted_data = json.dumps(
            data,
            indent=4,
            ensure_ascii=False,
            default=str,
        )
    except (TypeError, ValueError):
        formatted_data = repr(data)

    logger.log(level, "%s\n%s", message, formatted_data)