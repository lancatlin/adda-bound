from linebot.models.events import MessageEvent
from linebot.models.sources import SourceUser
from linebot.models.messages import TextMessage


def room_source(room):
    return SourceUser(user_id=room.room_id)


def sample_event(room, msg):
    '''Return a sample text message event'''
    return MessageEvent(source=room_source(
        room), message=TextMessage(text=msg))
