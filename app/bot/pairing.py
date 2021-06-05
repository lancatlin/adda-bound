from core.models import Pairing

from .line import reply_text, push_message
from .utils import with_room, get_token


@with_room
def create_pairing(event, room):
    print(room.name)
    pairing = Pairing.objects.create(room=room)
    reply_text(
        event,
        'Please copy the following message,\
and ask your recipient to send it to AddaBound.')
    push_message(room, f'/join {pairing.token}')


@with_room
def join_pairing(event, room):
    print(room.name)
    try:
        token = get_token(event.message.text)
        pairing = Pairing.objects.get(token=token)
        pair_with = pairing.room
        room.rooms.add(pair_with)
        print(room.rooms.all())
        pairing.delete()
        reply_text(event, f'Success connected with {pair_with.name}.')
        push_message(pair_with, f'Success connected with {room.name}.')

    except ValueError:
        reply_text(event, 'Cannot identify token from you command.')

    except Pairing.DoesNotExist:
        reply_text(event, 'Pairing not found.')
