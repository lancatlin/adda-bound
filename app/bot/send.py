import uuid

from linebot.models.template import ConfirmTemplate, TemplateSendMessage
from linebot.models.actions import PostbackAction

from core.models import Room

from .utils import parse_message, with_room
from .line import reply_text, push_message, line_bot_api
from .message_queue import MessageQueue


message_queue = MessageQueue()


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
    except Room.MultipleObjectsReturned:
        rooms = Room.objects.filter(name__icontains=recipient_name).all()
        rooms_name = ', '.join([room.name for room in rooms])
        reply_text(event, f'Found multiple recipients: {rooms_name}')


@with_room
def confirm_message(event, room):
    msg = event.postback.data
    try:
        msg_id = msg.split(' ')[1]
        if not message_queue.contain(msg_id):
            raise Exception('Message not found')

        msg = message_queue.get(msg_id)
        sender = msg['sender']
        recipient = msg['recipient']
        message = msg['message']
        push_message(
            recipient,
            f'from {sender.name}: {message}'
        )
        reply_text(event, 'Sent')
        message_queue.delete(msg_id)

    except Exception as e:
        reply_text(event, str(e))


@with_room
def del_message(event, room):
    msg = event.postback.data
    try:
        msg_id = msg.split(' ')[1]
        if msg_id in message_queue:
            message_queue.delete(msg_id)
            reply_text(event, 'Canceled')
        else:
            reply_text(event, 'Message not exists or already canceled')
    except Exception as e:
        reply_text(event, str(e))


@with_room
def confirm(event, room, recipient, message):
    '''Ask user to comfirm the message being sent'''
    msg_id = str(uuid.uuid4())
    message_queue.set(msg_id, {
        'sender': room,
        'recipient': recipient,
        'message': message,
    })
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
