from django.test import TestCase
from unittest.mock import patch

from threading import Thread

from bot.message_queue import (
    MessageQueue, RequestTimout
)
from core.tests.test_models import sample_room
from bot.tests.test_line import sample_event


class QueueTest(TestCase):
    def setUp(self):
        self.room = sample_room(name='TestRoom', room_id='12345656')

    def test_put_message(self):
        '''Test put the message into queue'''
        msg = 'test message'

        def req():
            res = MessageQueue.request(self.room)
            self.assertEqual(res.message.text, msg)

        thread = Thread(target=req)
        thread.start()
        MessageQueue.handle(sample_event(self.room, msg))
        thread.join()

    def test_not_to_put_message(self):
        '''Test ignore the message when no request'''
        msg = 'test message'
        MessageQueue.handle(sample_event(self.room, msg))
        self.assertTrue(MessageQueue._responses[self.room.id].empty())

    @patch('queue.time')
    def test_request_message_timeout(self, mock_time):
        '''Test request some message but timeout'''
        mock_time.side_effect = [0, 180]
        self.assertRaises(
            RequestTimout,
            lambda: MessageQueue.request(self.room),
        )
        self.assertEqual(mock_time.call_count, 2)
