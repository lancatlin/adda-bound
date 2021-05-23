import re
from core.models import Room


def get_token(msg):
    matches = re.findall(r"\d+", msg)
    if len(matches) != 1:
        raise ValueError('Their should be only one number')
    return int(matches[0])


def parse_message(msg):
    pieces = msg.split(' ')
    if len(pieces) < 2:
        raise ValueError('Cannot split recipient from message')
    return pieces[1], ' '.join(pieces[2:])


def with_room(callback):
    def func(event, *args):
        src = event.source
        if src.type == 'user':
            room = Room.objects.get(
                room_id=src.user_id,
                room_type=Room.RoomType.USER,
            )

        elif src.type == 'group':
            room = Room.objects.get(
                room_id=src.group_id,
                room_type=Room.RoomType.GROUP,
            )

        callback(event, room, *args)
    return func
