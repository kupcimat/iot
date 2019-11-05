import logging
import time


def with_retry(callback, callback_name, exception, count=3, sleep=1):
    for i in range(count):
        try:
            return callback()
        except exception:
            logging.debug("action=retry callback=%s exception=%s count=%s", callback_name, exception.__name__, i)
            time.sleep(sleep)
