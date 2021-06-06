from linebot.models.template import ConfirmTemplate, TemplateSendMessage
from linebot.models.actions import MessageAction

import queue

from core.models import Room

from .utils import parse_message, get_or_create_room
from .line import reply_text, push_message, line_bot_api
from .message_queue import MessageQueue


class Sender:
    def __init__(self, event):
        self.event = event
        self.room = get_or_create_room(event)
        self.request = event.message.text.strip()

    def reply(self, msg):
        reply_text(self.event, msg)

    def handle(self):
        try:
            if self.request == '/send':
                self.send_conversation()
            else:
                self.send()
        except ValueError:
            '''Parse error'''
            self.reply('Cannot parse the message')

        except Room.DoesNotExist:
            '''Room not found'''
            self.reply('Recipient not found')

        except Room.MultipleObjectsReturned:
            '''Found multiple rooms'''
            rooms = self.room.rooms.filter(
                name__icontains=self.recipient_name).all()
            rooms_name = ', '.join([room.name for room in rooms])
            self.reply(f'Found multiple recipients: {rooms_name}')

        except queue.Empty:
            '''Timeout'''
            push_message(self.room, 'Timeout, cancel')

    def send(self):
        self.recipient_name, self.content = parse_message(self.request)
        self.recipient = self.room.rooms.get(
            name__icontains=self.recipient_name)
        self.confirm()

    def ask(self, question):
        self.reply(question)
        self.event = MessageQueue.request(self.room)
        return self.event.message.text

    def send_conversation(self):
        self.recipient_name = self.ask('Recipient\'s name?')

        print(self.recipient_name)
        self.recipient = self.room.rooms.get(
            name__icontains=self.recipient_name)

        self.content = self.ask('Message?')

        self.confirm()

    def confirm(self):
        '''Ask user to comfirm the message being sent'''
        line_bot_api.reply_message(
            self.event.reply_token,
            TemplateSendMessage(
                alt_text='Confirm',
                template=ConfirmTemplate(
                    text=f'Send {self.recipient.name} "{self.content}" ?',
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
        res = MessageQueue.request(self.room)
        if res.message.text == 'Yes':
            push_message(self.recipient,
                         f'From {self.room.name}: {self.content}')
            reply_text(res, 'Sent')
        else:
            reply_text(res, 'Cancel')
