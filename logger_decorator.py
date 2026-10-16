"""
Name: Camea Hoffman
Assignment: a09
Description: Logging decorator for the social network project.

This module sets up application-wide logging to the file `assignment9.log`.
It defines a `log_decorator` that can be applied to any function to
automatically log when the function is called, whether it succeeds, and
any exceptions that occur.
"""

import logging

#pylint: disable=logging-fstring-interpolation

# Configure logging for the application
logging.basicConfig(
    filename="assignment9.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def log_decorator(func):
    """
    Decorator that logs function calls, successes, and failures.

    - Logs an INFO message before the function is called.
    - Logs an INFO message if the function completes successfully.
    - Logs an ERROR message and re-raises the exception if the function fails.

    Args:
        func (Callable): The function being decorated.

    Returns:
        Callable: Wrapped function that includes logging behavior.
    """
    def wrapper(*args, **kwargs):
        logger.info(f"Calling {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"{func.__name__} succeeded")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed: {e}")
            raise
    return wrapper
