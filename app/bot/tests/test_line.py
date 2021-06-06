from unittest.mock import patch
import time

from django.test import TestCase

from threading import Thread

from linebot.models.events import MessageEvent, PostbackEvent, Postback
from linebot.models.sources import SourceUser
from linebot.models.messages import TextMessage

from core.tests.test_models import sample_room

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
        self.room1 = sample_room(name='Cambridge', room_id='123456')
        self.room2 = sample_room(name='CyberPunk', room_id='345678')
        self.room3 = sample_room(name='CyberSpace', id='74747474')
        self.room1.rooms.add(self.room2, self.room3)

    @patch('bot.send.confirm')
    @patch('bot.send.push_message')
    @patch('bot.send.reply_text')
    def test_send_success(self, mock_reply, mock_push, mock_confirm):
        msg = 'This is my message'

        def func():
            time.sleep(0.1)
            event = sample_event(self.room1, 'Yes')
            handle(event)

        thread = Thread(target=func)
        thread.start()

        event = sample_event(self.room1, f'/send {self.room2.name} {msg}')
        handle(event)

        mock_confirm.assert_called_once_with(
            event, f'Send {self.room2.name} "{msg}" ?')
        mock_reply.assert_called_once_with(
            event, 'Sent',
        )
        mock_push.assert_called_once_with(
            self.room2, msg,
        )

        thread.join()

    # @patch('bot.send.reply_text')
    # def test_send_not_found_recipient(self, mock_reply):
    #     msg = '/send Derek This is my message'
    #     event = sample_event(self.room1, msg)
    #     send(event)
    #     mock_reply.assert_called_once_with(
    #         event, 'Recipient not found'
    #     )

    # @patch('bot.send.reply_text')
    # def test_send_found_multiple_recipients(self, mock_reply):
    #     '''Test found multiple recipients and should failed'''
    #     msg = '/send Cyber This is my message'
    #     event = sample_event(self.room1, msg)
    #     send(event)
    #     mock_reply.assert_called_once_with(
    #         event, 'Found multiple recipients: CyberPunk, CyberSpace'
    #     )

    # @patch('bot.send.reply_text')
    # @patch('bot.send.push_message')
    # def test_handle_user_confirm(self, mock_push, mock_reply):
    #     msg_id = '123456'
    #     message_queue.set(msg_id, {
    #         'sender': self.room1,
    #         'recipient': self.room2,
    #         'message': 'Hi, how are you?',
    #     })
    #     event = PostbackEvent(
    #         source=room_source(self.room1),
    #         postback=Postback(
    #             data=f'/confirm {msg_id}'
    #         )
    #     )
    #     confirm_message(event)

    #     mock_push.assert_called_once_with(
    #         self.room2,
    #         f'from {self.room1.name}: Hi, how are you?',
    #     )
    #     mock_reply.assert_called_once_with(event, 'Sent')
    #     self.assertFalse(message_queue.contain(msg_id))
