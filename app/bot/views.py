from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from linebot import WebhookHandler
from linebot.models.events import (
    MessageEvent, FollowEvent, JoinEvent, PostbackEvent
)
from linebot.models.messages import TextMessage

from .send import Sender
from .message_queue import MessageQueue, OtherCommandExecuting, RequestTimout
from .pairing import create_pairing, join_pairing
from .manage import Manager, PairingRemover
from .line import reply_text, push_message
from .utils import with_room, get_or_create_room

handler = WebhookHandler(settings.LINE_SECRET)


@csrf_exempt
def line_endpoint(request):
    if request.method == 'POST':
        signatrue = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        handler.handle(body, signatrue)

    return HttpResponse()


@handler.add(MessageEvent, message=TextMessage)
def handle(event):
    room = get_or_create_room(event)
    try:
        msg = event.message.text
        if msg.startswith('/create'):
            return create_pairing(event)

        if msg.startswith('/join'):
            return join_pairing(event)

        if msg.startswith('/send'):
            return Sender(event).handle()

        if msg.startswith('/manage'):
            return Manager(event).handle()

        if msg.startswith('/help'):
            return usage(event)

        if msg.startswith('/delete'):
            return reply_text(event, 'delete my information')

        MessageQueue.handle(event)

    except RequestTimout:
        '''Timeout'''
        push_message(room, '操作逾時，取消操作')

    except OtherCommandExecuting:
        '''There are other commands are processing'''
        push_message(room, '請先完成先前的操作')

    except Exception as e:
        room = get_or_create_room(event)
        push_message(room, "伺服器發生錯誤")
        raise e


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
def join_group(event):
    '''Join a group'''
    greeting(event)


@handler.add(PostbackEvent)
def del_room(event):
    PairingRemover(event).handle()


def usage(event):
    with open('usage.md', 'r') as f:
        msg = f.read()
        reply_text(event, msg)
