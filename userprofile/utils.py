def has_value(value):
    """
    We want values like 0 and False to be considered values, but values like
    None or blank strings to not be considered values
    """
    return value or value == 0 or value is False
