import functools
import sys

from lib.loggerinit import logger_init

# Wrap the function to include start and end logs, and time elapsed.


logger = logger_init(__name__)


def log_time(func):
    @functools.wraps(func)
    def func_wrapper(*args, **kwargs):
        import time

        s = time.perf_counter()
        logger.info(
            "STARTING NEW RUN at %s", time.strftime("%m/%d/%Y, %H:%M:%S")
        )

        assert sys.version_info >= (3, 7), "Script requires Python 3.7+."

        func(*args, **kwargs)

        elapsed = time.perf_counter() - s
        logger.info("RUN COMPLETE. Executed in %0.2f seconds", elapsed)

    return func_wrapper
