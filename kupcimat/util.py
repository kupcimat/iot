import functools
import logging
import time


def with_retry(callback, callback_name, exception, count=3, sleep=1):
    for i in range(count - 1):
        try:
            return callback()
        except Exception as e:
            logging.debug("action=retry callback=%s exception=%s attempt=%s message=%s",
                          callback_name, exception.__name__, i, e)
            time.sleep(sleep)
    return callback()


# TODO remove when upgrading to python 3.8
def unwrap_partial(func):
    if isinstance(func, functools.partial):
        return unwrap_partial(func.func)
    return func


def unwrap_dict(dictionary):
    (name, properties), = dictionary.items()
    return name, properties
