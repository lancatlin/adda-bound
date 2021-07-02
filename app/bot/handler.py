from linebot.models.send_messages import QuickReply, QuickReplyButton, TextSendMessage
from linebot.models.actions import MessageAction

from .message_queue import MessageQueue
from .utils import get_user_name, get_or_create_room
from .line import reply_text, line_bot_api
from core.models import Room


class Cancel(Exception):
    pass


class BaseHandler:
    def __init__(self, event):
        self.event = event
        self.room = get_or_create_room(event)

    def request(self):
        result = self.event.message.text.strip()
        if result == '/cancel':
            raise Cancel
        return result

    def reply(self, *msg, **kwargs):
        reply_text(self.event, *msg, **kwargs)

    def sender_name(self):
        if self.room.room_type == Room.RoomType.GROUP:
            user_id = self.event.source.user_id
            user_name = get_user_name(user_id)
            return f'{user_name}在{self.room.name}'
        return self.room.name

    def handle(self):
        pass

    def ask(self, *question):
        self.reply(*question)
        self.event = MessageQueue.request(self.room)
        return self.request()

    def confirm(self, msg):
        '''Ask user to comfirm the message being sent'''
        line_bot_api.reply_message(
            self.event.reply_token,
            TextSendMessage(
                text=msg,
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(
                                label=text, text=text,
                            )
                        ) for text in ['是', '否']
                    ]
                )
            ),
            notification_disabled=True,
        )
        self.event = MessageQueue.request(self.room)
        return self.event.message.text == '是'
