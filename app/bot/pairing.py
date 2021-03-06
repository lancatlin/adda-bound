from core.models import Pairing

from .line import reply_text, push_message
from .utils import with_room, get_token


@with_room
def create_pairing(event, room):
    pairing = Pairing.objects.create(room=room)
    reply_text(
        event,
        '請複製下方訊息，請你要連線的對象傳送此訊息給 AddaBound',
        f'/join {pairing.token}'
    )


@with_room
def join_pairing(event, room):
    try:
        token = get_token(event.message.text)
        pairing = Pairing.objects.get(token=token)
        pair_with = pairing.room
        room.rooms.add(pair_with)
        pairing.delete()
        reply_text(event, f'成功與 {pair_with.name} bound 在一起！')
        push_message(pair_with, f'成功與 {room.name} bound 在一起！')

    except ValueError:
        reply_text(event, '無法從訊息中找到配對碼')

    except Pairing.DoesNotExist:
        reply_text(event, '找不到配對')
