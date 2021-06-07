from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from linebot import WebhookHandler
from linebot.models.events import (MessageEvent, FollowEvent, JoinEvent)
from linebot.models.messages import TextMessage

from .send import Sender
from .message_queue import MessageQueue
from .pairing import create_pairing, join_pairing
from .manage import manage
from .line import reply_text
from .utils import with_room

handler = WebhookHandler(settings.LINE_SECRET)


@csrf_exempt
def line_endpoint(request):
    if request.method == 'POST':
        signatrue = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        print(body)
        handler.handle(body, signatrue)

    return HttpResponse()


@handler.add(MessageEvent, message=TextMessage)
def handle(event):
    msg = event.message.text
    if msg.startswith('/create'):
        return create_pairing(event)

    if msg.startswith('/join'):
        return join_pairing(event)

    if msg.startswith('/send'):
        return Sender(event).handle()

    if msg.startswith('/manage'):
        return manage(event)

    if msg.startswith('/delete'):
        return reply_text(event, 'delete my information')

    MessageQueue.handle(event)


@with_room
def greeting(event, room):
    '''Greeting when join
    created is whether has created a new room
    '''
    reply_text(event, f'哈囉 {room.name}！謝謝你使用 AddaBound')


@handler.add(FollowEvent)
def join_user(event):
    '''A user add the bot'''
    greeting(event)


@handler.add(JoinEvent)
def join_group(event, room):
    '''Join a group'''
    greeting(event)
