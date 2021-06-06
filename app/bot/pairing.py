from core.models import Pairing

from .line import reply_text, push_message
from .utils import with_room, get_token


@with_room
def create_pairing(event, room):
    print(room.name)
    pairing = Pairing.objects.create(room=room)
    reply_text(
        event,
        '請複製下方訊息，請你欲連線者傳送此訊息給 AddaBound',
        f'/join {pairing.token}'
    )


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
        reply_text(event, f'成功與 {pair_with.name} 建立連線')
        push_message(pair_with, f'成功與 {room.name} 建立連線')

    except ValueError:
        reply_text(event, '無法從訊息中找到配對碼')

    except Pairing.DoesNotExist:
        reply_text(event, '找不到配對')
