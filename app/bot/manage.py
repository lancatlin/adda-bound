from linebot.models.template import TemplateSendMessage, ButtonsTemplate
from linebot.models.actions import PostbackAction

from .handler import BaseHandler
from .message_queue import MessageQueue
from .line import line_bot_api


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
