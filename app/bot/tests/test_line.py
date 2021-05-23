from unittest.mock import patch

from django.test import TestCase

from linebot.models.events import MessageEvent, PostbackEvent, Postback
from linebot.models.sources import SourceUser
from linebot.models.messages import TextMessage

from core.tests.test_models import sample_room

from bot.send import send, confirm, message_queue, confirm_message


def room_source(room):
    return SourceUser(user_id=room.room_id)


class LineBotTest(TestCase):
    def setUp(self):
        self.room1 = sample_room(name='CyberPunk', room_id='123456')
        self.room2 = sample_room(name='Cambridge', room_id='345678')
        self.room1.rooms.add(self.room2)

    @patch('uuid.uuid4')
    @patch('bot.line.line_bot_api.reply_message')
    def test_confirm(self, mock_reply, mock_uuid):
        uuid = '123456'
        mock_uuid.return_value = uuid
        event = MessageEvent(source=room_source(self.room1))
        msg = 'This is my message'
        confirm(event, self.room2, msg)
        mock_reply.assert_called_once()
        mock_uuid.assert_called_once()
        self.assertIn(uuid, message_queue)
        self.assertEqual(message_queue[uuid], {
            'sender': self.room1,
            'recipient': self.room2,
            'message': msg,
        })

    @patch('bot.send.confirm')
    def test_send_success(self, mock_confirm):
        msg = f'/send {self.room2.name} This is my message'
        event = MessageEvent(source=room_source(
            self.room1), message=TextMessage(text=msg))
        send(event)
        mock_confirm.assert_called_once_with(
            event, self.room2, 'This is my message')

    @patch('bot.send.reply_text')
    def test_send_not_found_recipient(self, mock_reply):
        msg = '/send Derek This is my message'
        event = MessageEvent(source=room_source(
            self.room1), message=TextMessage(text=msg))
        send(event)
        mock_reply.assert_called_once_with(
            event, 'Recipient not found'
        )

    @patch('bot.send.reply_text')
    @patch('bot.send.push_message')
    def test_handle_user_confirm(self, mock_push, mock_reply):
        msg_id = '123456'
        message_queue[msg_id] = {
            'sender': self.room1,
            'recipient': self.room2,
            'message': 'Hi, how are you?',
        }
        event = PostbackEvent(
            source=room_source(self.room1),
            postback=Postback(
                data=f'/confirm {msg_id}'
            )
        )
        confirm_message(event)

        mock_push.assert_called_once_with(
            self.room2,
            f'from {self.room1.name}: Hi, how are you?',
        )
        mock_reply.assert_called_once_with(event, 'Sent')
        self.assertNotIn(msg_id, message_queue)
