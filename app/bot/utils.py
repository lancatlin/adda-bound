import re


def get_token(msg):
    matches = re.findall(r"\d+", msg)
    if len(matches) != 1:
        raise ValueError('Their should be only one number')
    return int(matches[0])
