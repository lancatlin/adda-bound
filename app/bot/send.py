from linebot.models.template import ConfirmTemplate, TemplateSendMessage
from linebot.models.actions import MessageAction

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
        confirm(event, f'Send {recipient.name} "{message}" ?')

        print('request')
        res = message_queue.request(room)
        print(res)
        if res.message.text == 'Yes':
            push_message(recipient, message)
            reply_text(res, 'Sent')
        else:
            reply_text(res, 'Cancel')
    except ValueError:
        reply_text(event, 'Cannot parse the message')
    except Room.DoesNotExist:
        reply_text(event, 'Recipient not found')
    except Room.MultipleObjectsReturned:
        rooms = Room.objects.filter(name__icontains=recipient_name).all()
        rooms_name = ', '.join([room.name for room in rooms])
        reply_text(event, f'Found multiple recipients: {rooms_name}')


@with_room
def confirm(event, room, message):
    '''Ask user to comfirm the message being sent'''
    line_bot_api.reply_message(
        event.reply_token,
        TemplateSendMessage(
            alt_text='Confirm',
            template=ConfirmTemplate(
                text=message,
                actions=[
                    MessageAction(
                        label='Yes',
                        text='Yes'
                    ),
                    MessageAction(
                        label='No',
                        text='No'
                    )
                ]
            )
        )
    )
