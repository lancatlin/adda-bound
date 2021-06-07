from linebot.models.template import ConfirmTemplate, TemplateSendMessage, ButtonsTemplate
from linebot.models.actions import MessageAction

import queue

from core.models import Room

from .utils import parse_message, get_or_create_room, get_user_name
from .line import reply_text, push_message, line_bot_api
from .message_queue import MessageQueue


class NoRecipientError(Exception):
    pass


class Sender:
    def __init__(self, event):
        self.event = event
        self.room = get_or_create_room(event)

    def request(self):
        return self.event.message.text.strip()

    def reply(self, *msg):
        reply_text(self.event, *msg)

    def sender_name(self):
        if self.room.room_type == Room.RoomType.GROUP:
            user_id = self.event.source.user_id
            user_name = get_user_name(user_id)
            return f'{user_name}在{self.room.name}'
        return self.room.name

    def handle(self):
        try:
            if self.request() == '/send':
                self.send_conversation()
            else:
                self.send_by_command()
        except ValueError:
            '''Parse error'''
            self.reply('無法解析訊息')

        except Room.DoesNotExist:
            '''Room not found'''
            self.reply('找不到收件者，取消操作')

        except Room.MultipleObjectsReturned:
            '''Found multiple rooms'''
            rooms = self.room.rooms.filter(
                name__icontains=self.recipient_name).all()
            rooms_name = '、'.join([room.name for room in rooms])
            self.reply(f'找到多位收件者：{rooms_name}，請重新操作')

        except queue.Empty:
            '''Timeout'''
            push_message(self.room, '操作逾時，取消操作')

        except NoRecipientError:
            self.reply('沒有已配對的聊天室')

    def send(self):
        if self.confirm():
            push_message(
                self.recipient,
                f'來自{self.sender_name()}的訊息：',
                self.content
            )
            self.reply('已傳送')
        else:
            self.reply('取消')

    def send_by_command(self):
        self.recipient_name, self.content = parse_message(self.request())
        self.recipient = self.room.rooms.get(
            name__icontains=self.recipient_name)
        self.send()

    def ask(self, *question):
        self.reply(*question)
        self.event = MessageQueue.request(self.room)
        return self.event.message.text

    def send_conversation(self):
        self.get_recipient()

        self.content = self.ask(
            f'收件人：{self.recipient.name}', '請輸入訊息內容')

        self.send()

    def get_recipient(self):
        actions = [
            MessageAction(
                label=room.name,
                text=room.name,
            )
            for room in self.room.rooms.all()
        ]
        print(actions)
        if not actions:
            raise NoRecipientError

        if len(actions) == 1:
            self.recipient = self.room.rooms.get()
            return

        line_bot_api.reply_message(
            self.event.reply_token,
            TemplateSendMessage(
                alt_text='Recipients',
                template=ButtonsTemplate(
                    text='請選取收件者：',
                    actions=actions,
                ),
            ),
        )
        self.event = MessageQueue.request(self.room)
        self.recipient = self.room.rooms.get(
            name__icontains=self.event.message.text)

    def confirm(self):
        '''Ask user to comfirm the message being sent'''
        line_bot_api.reply_message(
            self.event.reply_token,
            TemplateSendMessage(
                alt_text='Confirm',
                template=ConfirmTemplate(
                    text=f'是否要發送「{self.content}」給{self.recipient.name}？',
                    actions=[
                        MessageAction(
                            label='是',
                            text='Yes'
                        ),
                        MessageAction(
                            label='取消',
                            text='No'
                        )
                    ]
                )
            )
        )
        self.event = MessageQueue.request(self.room)
        return self.request().lower() == 'yes'
