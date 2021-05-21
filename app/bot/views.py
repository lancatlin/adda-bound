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

from core.models import Room


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
def echo(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text)
    )


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
        room_type=Room.RoomType.Group,
        defaults={'service': Room.Service.LINE,
                  'name': get_group_name(src.group_id)},
    )
    greeting(event, room, created)
