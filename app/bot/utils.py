import re
from .line import get_user_name, get_group_name
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


def get_or_create_room(event):
    src = event.source
    if src.type == 'user':
        room_id = src.user_id
        room_type = Room.RoomType.USER
        name = get_user_name(src.user_id)

    elif src.type == 'group':
        room_id = src.group_id
        room_type = Room.RoomType.GROUP
        name = get_group_name(src.group_id)

    # room = Room.objects.get(
    #     room_id=room_id,
    #     room_type=room_type,
    #     service=Room.Service.LINE,
    # )
    room, created = Room.objects.get_or_create(
        room_id=room_id,
        defaults={
            'name': name,
            'room_type': room_type,
            'service': Room.Service.LINE,
        },
    )
    if created:
        print('created', room.__dict__)
    return room


def with_room(callback):
    def func(event, *args):
        return callback(event, get_or_create_room(event), *args)
    return func
