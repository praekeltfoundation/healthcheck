import re


def normalise_text(text: str) -> str:
    """
    Returns text in title case, with only a single space between words, and no leading
    or trailing whitespace.
    """
    return re.sub(r"\s+", " ", text).strip().title()
