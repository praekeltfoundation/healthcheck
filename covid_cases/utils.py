import os
import re
from functools import wraps
from urllib.parse import urlparse

from django.core.cache import cache


def normalise_text(text: str) -> str:
    """
    Returns text in title case, with only a single space between words, and no leading
    or trailing whitespace.
    """
    return re.sub(r"\s+", " ", text).strip().title()


def get_filename_from_url(url: str) -> str:
    url = urlparse(url)
    return os.path.basename(url.path)


def cache_method(key, expiry):
    """
    Uses django caching to cache the result from a method in a static key. Note that the
    cached value doesn't change according to function arguments
    """

    def wrapper(function):
        @wraps(function)
        def inner(*args, **kwargs):
            result = cache.get(key)
            if result:
                return result
            result = function(*args, **kwargs)
            cache.set(key, result, expiry)
            return result

        return inner

    return wrapper
