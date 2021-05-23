import uuid

from django.conf import settings
from linebot import LineBotApi, WebhookHandler
from linebot.models.messages import TextMessage
from linebot.models.events import (
    MessageEvent, FollowEvent, JoinEvent, PostbackEvent)
from linebot.models.send_messages import TextSendMessage
from linebot.models.template import ConfirmTemplate, TemplateSendMessage
from linebot.models.actions import PostbackAction

from core.models import Room, Pairing

from bot.utils import get_token, parse_message

line_bot_api = LineBotApi(settings.LINE_TOKEN)
handler = WebhookHandler(settings.LINE_SECRET)

message_queue = {}


def with_room(callback):
    def func(event, *args):
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

        callback(event, room, *args)
    return func


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


@handler.add(PostbackEvent)
@with_room
def postback_confirm(event, room, *args):
    print(message_queue)
    msg = event.postback.data
    try:
        msg_id = msg.split(' ')[1]
        print(msg_id)
        if msg_id not in message_queue:
            raise Exception('Message not found')

        msg = message_queue[msg_id]
        sender = msg['sender']
        recipient = msg['recipient']
        message = msg['message']
        push_message(
            recipient,
            f'from {sender.name}: {message}'
        )
        reply_text(event, 'Sent')
        del message_queue[msg_id]

    except Exception as e:
        print(e)
        reply_text(event, 'Message not found')


@with_room
def create_pairing(event, room):
    print(room.name)
    pairing = Pairing.objects.create(room=room)
    reply_text(event, f'create new pairing {pairing.token}')


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

    except ValueError:
        reply_text(event, 'Cannot identify token from you command.')

    except Pairing.DoesNotExist:
        reply_text(event, 'Pairing not found.')


@with_room
def manage(event, room):
    msg = event.message.text
    if msg == '/manage list':
        rooms_name = [
            room.name for room in room.rooms.all()
        ]
        reply_text(event, '\n'.join(rooms_name))


@with_room
def send(event, room):
    msg = event.message.text
    try:
        recipient_name, message = parse_message(msg)
        recipient = room.rooms.get(name__icontains=recipient_name)
        confirm(event, recipient, message)
    except ValueError:
        reply_text(event, 'Cannot parse the message')
    except Room.DoesNotExist:
        reply_text(event, 'Recipient not found')


def push_message(room, msg):
    line_bot_api.push_message(
        room.room_id,
        TextSendMessage(text=msg)
    )


def get_user_name(user_id):
    try:
        res = line_bot_api.get_profile(user_id)
        return res.display_name
    except Exception:
        return 'NoNameUser'


def get_group_name(group_id):
    try:
        res = line_bot_api.get_group_summary(group_id)
        return res.group_name
    except Exception:
        return 'NoNameGroup'


def reply_text(event, message):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message)
    )


@with_room
def confirm(event, room, recipient, message):
    '''Ask user to comfirm the message being sent'''
    msg_id = str(uuid.uuid4())
    message_queue[msg_id] = {
        'sender': room,
        'recipient': recipient,
        'message': message,
    }
    line_bot_api.reply_message(
        event.reply_token,
        TemplateSendMessage(
            alt_text='Confirm',
            template=ConfirmTemplate(
                text=f'Send {recipient.name} "{message}" ?',
                actions=[
                    PostbackAction(
                        label='Yes',
                        data=f'/confirm {msg_id}',
                        display_text='Yes'
                    ),
                    PostbackAction(
                        label='No',
                        data=f'/del {msg_id}',
                        display_text='No'
                    )
                ]
            )
        )
    )
    print(message_queue)


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
