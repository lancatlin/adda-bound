from unittest.mock import patch

from django.test import TestCase

from linebot.models.events import MessageEvent
from linebot.models.sources import SourceUser
from linebot.models.messages import TextMessage

from core.tests.test_models import sample_room

from bot.line import send


def room_source(room):
    return SourceUser(user_id=room.room_id)


class LineBotTest(TestCase):
    def setUp(self):
        self.room1 = sample_room(name='CyberPunk', room_id='123456')
        self.room2 = sample_room(name='Cambridge', room_id='345678')
        self.room1.rooms.add(self.room2)

    @patch('bot.line.reply_text')
    @patch('bot.line.push_message')
    def test_send_success(self, mock_push, mock_reply):
        msg = f'/send {self.room2.name} This is my message'
        event = MessageEvent(source=room_source(
            self.room1), message=TextMessage(text=msg))
        send(event)
        mock_push.assert_called_once_with(self.room2, 'This is my message')
        mock_reply.assert_called_once_with(
            event, f'Sent {self.room2.name} "This is my message"')

    @patch('bot.line.reply_text')
    @patch('bot.line.push_message')
    def test_send_not_found_recipient(self, mock_push, mock_reply):
        msg = '/send Derek This is my message'
        event = MessageEvent(source=room_source(
            self.room1), message=TextMessage(text=msg))
        send(event)
        mock_push.assert_not_called()
        mock_reply.assert_called()
