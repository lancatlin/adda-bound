from linebot.models.template import (
    ConfirmTemplate, TemplateSendMessage, ButtonsTemplate)
from linebot.models.actions import MessageAction
from linebot.models.send_messages import QuickReply, QuickReplyButton, TextSendMessage

import queue

from core.models import Room

from .utils import parse_message
from .line import push_message, line_bot_api
from .message_queue import MessageQueue
from .handler import BaseHandler


class NoRecipientError(Exception):
    pass


class OtherCommandExecuting(Exception):
    pass


class Sender(BaseHandler):
    def handle(self):
        try:
            if not MessageQueue.available(self.room):
                raise OtherCommandExecuting()
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
            MessageQueue.clear(self.room)
            push_message(self.room, '操作逾時，取消操作')

        except OtherCommandExecuting:
            '''There are other commands are processing'''
            self.reply('請先完成先前的操作')

        except NoRecipientError:
            self.reply('沒有已配對的聊天室')

    def send(self):
        push_message(
            self.recipient,
            f'來自{self.sender_name()}的訊息：',
            self.content
        )
        self.reply('已傳送')

    def send_by_command(self):
        self.recipient_name, self.content = parse_message(self.request())
        self.recipient = self.room.rooms.get(
            name__icontains=self.recipient_name)
        self.send()

    def send_conversation(self):
        self.get_recipient()

        self.reply(f'收件人：{self.recipient.name}', '請輸入訊息內容')

        self.event = MessageQueue.request(self.room, timeout=300)
        self.content = self.request()

        self.send()

    def get_recipient(self):
        items = [
            QuickReplyButton(action=MessageAction(
                label=room.name,
                text=room.name,
            ))
            for room in self.room.rooms.all()
        ]
        print(items)
        if not items:
            raise NoRecipientError

        if len(items) == 1:
            self.recipient = self.room.rooms.get()
            return

        line_bot_api.reply_message(
            self.event.reply_token,
            messages=TextSendMessage(
                text='選取收件人：',
                quick_reply=QuickReply(
                    items=items,
                )),
            notification_disabled=True,
        )
        self.event = MessageQueue.request(self.room)
        self.recipient = self.room.rooms.get(
            name__icontains=self.event.message.text)
