from django.conf import settings

from linebot import WebhookHandler
from linebot.models.events import (
    MessageEvent, FollowEvent, JoinEvent, PostbackEvent)
from linebot.models.messages import TextMessage

from .send import send, confirm_message, del_message
from .pairing import create_pairing, join_pairing
from .manage import manage
from .line import reply_text
from .utils import with_room

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


@handler.add(PostbackEvent)
def postback_handler(event, *args):
    msg = event.postback.data
    if msg.startswith('/confirm'):
        return confirm_message(event)

    if msg.startswith('/del'):
        del_message(event)


@with_room
def greeting(event, room):
    '''Greeting when join
    created is whether has created a new room
    '''
    reply_text(event, f'Hello {room.name}! Thanks for using AddaBound')


@handler.add(FollowEvent)
def join_user(event):
    '''A user add the bot'''
    greeting(event)


@handler.add(JoinEvent)
def join_group(event, room):
    '''Join a group'''
    greeting(event)
