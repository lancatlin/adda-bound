from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FollowEvent, JoinEvent
)

from core.models import Room, Pairing


line_bot_api = LineBotApi(settings.LINE_TOKEN)
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
        return reply_text(event, 'join a pairing')

    if msg.startswith('/manage'):
        return reply_text(event, 'manage the pairings')

    if msg.startswith('/delete'):
        return reply_text(event, 'delete my information')

    reply_text(event, msg)


def with_room(callback):
    def func(event):
        src = event.source
        if src.type == 'user':
            room = Room.objects.get(
                room_id=src.user_id,
                room_type=Room.RoomType.USER,
            )

        elif src.type == 'group':
            room = Room.objects.get(
                room_id=src.group_id,
                room_type=Room.RoomType.GROUP,
            )

        callback(event, room)
    return func


@with_room
def create_pairing(event, room):
    print(room.name)
    pairing = Pairing.objects.create(room=room)
    reply_text(event, f'create new pairing {pairing.token}')


def get_user_name(user_id):
    try:
        res = line_bot_api.get_profile(user_id)
        return res.display_name
    except Exception as e:
        return 'NoNameUser'


def get_group_name(group_id):
    try:
        res = line_bot_api.get_group_summary(group_id)
        return res.group_name
    except Exception as e:
        return 'NoNameGroup'


def reply_text(event, message):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message)
    )


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
