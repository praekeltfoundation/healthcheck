import os
import re
from urllib.parse import urlparse


def normalise_text(text: str) -> str:
    """
    Returns text in title case, with only a single space between words, and no leading
    or trailing whitespace.
    """
    return re.sub(r"\s+", " ", text).strip().title()


def get_filename_from_url(url: str) -> str:
    url = urlparse(url)
    return os.path.basename(url.path)
