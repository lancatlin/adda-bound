from django.test import TestCase

from threading import Thread
import time

from bot.queue import MessageQueue
from core.tests.test_models import sample_room
from bot.tests.test_line import sample_event


class QueueTest(TestCase):
    def setUp(self):
        self.room = sample_room(name='TestRoom', id='12345656')
        self.queue = MessageQueue()

    def test_put_message(self):
        '''Test put the message into queue'''
        msg = 'test message'

        def req():
            res = self.queue.request(self.room)
            self.assertEqual(res, msg)

        thread = Thread(target=req)
        thread.start()
        self.queue.handle(sample_event(self.room, msg))
        thread.join()

    def test_not_to_put_message(self):
        '''Test ignore the message when no request'''
        msg = 'test message'
        self.queue.handle(sample_event(self.room, msg))
        self.assertTrue(self.queue._responses[self.room.id].empty())

    def test_request_message(self):
        '''Test request some message and get one'''

    def test_request_message_timeout(self):
        '''Test request some message but timeout'''
