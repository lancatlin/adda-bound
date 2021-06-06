import queue
from threading import Lock

from .utils import get_room


class MessageQueue:
    def __init__(self):
        self._requests = {}
        self._responses = {}

    def create_if_not_exists(self, room):
        if room.id not in self._requests:
            self._requests[room.id] = queue.Queue(maxsize=1)

        if room.id not in self._responses:
            self._responses[room.id] = queue.Queue(maxsize=1)

    def handle(self, event):
        room = get_room(event)
        self.create_if_not_exists(room)

        try:
            if self._requests[room.id].get_nowait():
                self._responses[room.id].put(event)
        except queue.Empty:
            '''No request, ignore the message'''
            pass

    def request(self, room):
        self.create_if_not_exists(room)

        self._requests[room.id].put_nowait(True)
        return self._responses[room.id].get(timeout=180)