from .utils import with_room
from .line import reply_text


@with_room
def manage(event, room):
    msg = event.message.text
    if msg == '/manage list':
        rooms_name = [
            room.name for room in room.rooms.all()
        ]
        reply_text(event, '\n'.join(rooms_name))
