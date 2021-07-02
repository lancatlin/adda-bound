from linebot.models.template import TemplateSendMessage, ButtonsTemplate
from linebot.models.actions import PostbackAction

from core.models import Room

from .handler import BaseHandler
from .message_queue import MessageQueue
from .line import line_bot_api, push_message
from .utils import get_token


class Manager(BaseHandler):
    def handle(self):
        rooms = self.room.rooms.all()
        if not rooms:
            return self.reply('目前沒有配對')

        line_bot_api.reply_message(
            reply_token=self.event.reply_token,
            messages=TemplateSendMessage(
                alt_text='Manage',
                template=ButtonsTemplate(
                    title='管理配對',
                    text='點擊要移除的配對，可多次點擊，無須操作請忽略訊息',
                    actions=[
                        PostbackAction(
                            label=f'移除 {room.name}',
                            display_text=f'移除 {room.name}',
                            data=f'/del {room.id}',
                        )
                        for room in rooms
                    ]
                )
            )
        )


class PairingRemover(BaseHandler):
    def request(self):
        return self.event.postback.data

    def handle(self):
        try:
            room_id = get_token(self.request())
            recipient = self.room.rooms.get(id=room_id)
            if self.confirm(f'確定要移除與{recipient.name}的配對嗎？（對方會收到通知）'):
                self.room.rooms.remove(recipient)
                self.reply(f'已經解除與{recipient.name}的配對')
                push_message(recipient, f'與{self.room.name}的配對已經被對方解除')
            else:
                self.reply('取消')
        except ValueError:
            self.reply('無法解析訊息')

        except Room.DoesNotExist:
            self.reply('找不到房間，或是房間已經被刪除了')
