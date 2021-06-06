from django.test import TestCase

from bot.queue import MessageQueue
from core.tests.test_models import sample_room


class QueueTest(TestCase):
    def setUp(self):
        self.room = sample_room(name='TestRoom', id='12345656')
        self.queue = MessageQueue()

    def test_put_message(self):
        '''Test put the message into queue'''

    def test_not_to_put_message(self):
        '''Test ignore the message when no request'''

    def test_request_message(self):
        '''Test request some message and get one'''

    def test_request_message_timeout(self):
        '''Test request some message but timeout'''
