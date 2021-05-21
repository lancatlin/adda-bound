import re


def get_token(msg):
    matches = re.findall(r"\d+", msg)
    if len(matches) != 1:
        raise ValueError('Their should be only one number')
    return int(matches[0])


def get_recipient(msg):
    pieces = msg.split(' ')
    if len(pieces) < 2:
        raise ValueError('Cannot split recipient from message')
    return pieces[1]
