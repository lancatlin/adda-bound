from django.conf import settings

from linebot import WebhookHandler
from linebot.models.events import (
    MessageEvent, FollowEvent, JoinEvent, PostbackEvent)
from linebot.models.messages import TextMessage

from core.models import Room

from .send import send, confirm_message, del_message
from .pairing import create_pairing, join_pairing
from .manage import manage
from .line import reply_text, get_user_name, get_group_name

handler = WebhookHandler(settings.LINE_SECRET)


@handler.add(MessageEvent, message=TextMessage)
def handle(event):
    msg = event.message.text
    if msg.startswith('/create'):
        return create_pairing(event)

    if msg.startswith('/join'):
        return join_pairing(event)

    if msg.startswith('/send'):
        return send(event)

    if msg.startswith('/manage'):
        return manage(event)

    if msg.startswith('/delete'):
        return reply_text(event, 'delete my information')

    reply_text(event, msg)


@handler.add(PostbackEvent)
def postback_handler(event, *args):
    msg = event.postback.data
    if msg.startswith('/confirm'):
        return confirm_message(event)

    if msg.startswith('/del'):
        del_message(event)


@handler.add(FollowEvent)
def join_user(event):
    '''A user add the bot'''
    print(event)
    src = event.source
    room, created = Room.objects.get_or_create(
        room_id=src.user_id,
        room_type=Room.RoomType.USER,
        defaults={'service': Room.Service.LINE,
                  'name': get_user_name(src.user_id)},
    )
    greeting(event, room, created)


@handler.add(JoinEvent)
def join_group(event):
    '''Join a group'''
    print(event)
    src = event.source
    room, created = Room.objects.get_or_create(
        room_id=src.group_id,
        room_type=Room.RoomType.GROUP,
        defaults={'service': Room.Service.LINE,
                  'name': get_group_name(src.group_id)},
    )
    greeting(event, room, created)


def greeting(event, room, created):
    '''Greeting when join
    created is whether has created a new room
    '''
    if created:
        '''New user'''
        reply_text(event, f'Hello {room.name}! Thanks for using AddaBound')
    else:
        '''Old user'''
        reply_text(
            event, f'Hi {room.name}, we are appreciate that you came back!')
