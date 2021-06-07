from .message_queue import MessageQueue
from .utils import get_user_name, get_or_create_room
from .line import reply_text
from core.models import Room


class BaseHandler:
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
        pass

    def ask(self, *question):
        self.reply(*question)
        self.event = MessageQueue.request(self.room)
        return self.event.message.text
