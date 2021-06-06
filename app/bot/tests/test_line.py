from unittest.mock import patch
import time

from django.test import TestCase
from django.db import transaction

from threading import Thread

from linebot.models.events import MessageEvent, PostbackEvent, Postback
from linebot.models.sources import SourceUser
from linebot.models.messages import TextMessage

from core.tests.test_models import sample_room
from core.models import Room

from bot.send import send
from bot.handler import handle


def room_source(room):
    return SourceUser(user_id=room.room_id)


def sample_event(room, msg):
    '''Return a sample text message event'''
    return MessageEvent(source=room_source(
        room), message=TextMessage(text=msg))


class LineBotTest(TestCase):
    def setUp(self):
        self.room1 = sample_room(name='Cambridge', room_id='cambridge')
        self.room1.save()
        self.room2 = sample_room(name='CyberPunk', room_id='345678')
        self.room2.save()
        self.room3 = sample_room(name='CyberSpace', room_id='74747474')
        self.room3.save()
        self.room1.rooms.add(self.room2, self.room3)
        transaction.commit()

    # @patch('bot.send.confirm')
    # @patch('bot.send.push_message')
    # @patch('bot.send.reply_text')
    # def test_send_success(self, mock_reply, mock_push, mock_confirm):
    #     msg = 'This is my message'
    #     print(self.room1.__dict__)

    #     def func():
    #         try:
    #             Room.objects.get(id=self.room1.id)
    #             event = sample_event(
    #                 self.room1, f'/send {self.room2.name} {msg}')
    #             handle(event)
    #         except Room.DoesNotExist:
    #             print('room1 does not exist')

    #     thread = Thread(target=func)
    #     thread.start()
    #     time.sleep(1)
    #     event = sample_event(self.room1, 'Yes')
    #     handle(event)

    #     mock_confirm.assert_called_once_with(
    #         event, f'Send {self.room2.name} "{msg}" ?')
    #     mock_reply.assert_called_once_with(
    #         event, 'Sent',
    #     )
    #     mock_push.assert_called_once_with(
    #         self.room2, msg,
    #     )

    #     thread.join()
