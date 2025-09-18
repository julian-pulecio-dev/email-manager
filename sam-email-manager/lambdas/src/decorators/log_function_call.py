import os
import functools
import logging
import time
import json
from datetime import datetime, timezone

LEVELS = {
    "CRITICAL": logging.CRITICAL,
    "FATAL": logging.FATAL,  # alias
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "WARN": logging.WARNING,  # alias
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
    "NOTSET": logging.NOTSET,
}

logger = logging.getLogger(__name__) 
logger_level_str = os.getenv("LOGGER_LEVEL", "INFO").upper()
logger.setLevel(LEVELS.get(logger_level_str, logging.INFO))


def safe_serialize(value):
    try:
        _ = json.dumps(value)
        return value
    except (TypeError, ValueError):
        str_val = str(value)
        if len(str_val) > 250:
            return str_val[:250] + "...(truncated)"
        return str_val


def log_function_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        serialized_args = [safe_serialize(arg) for arg in args]
        serialized_kwargs = {k: safe_serialize(v) for k, v in kwargs.items()}

        logger.debug(json.dumps({
            "event": "function_call",
            "function": func.__name__,
            "args": serialized_args,
            "kwargs": serialized_kwargs
        }))

        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = (time.perf_counter() - start) * 1000

        logger.debug(json.dumps({
            "event": "function_return",
            "function": func.__name__,
            "result": safe_serialize(result),
            "elapsed_ms": round(elapsed, 2)
        }))
        return result

    return wrapper
