import queue
from threading import RLock

from .utils import get_or_create_room


class MessageQueue:
    _lock = RLock()
    _requests = {}
    _responses = {}

    @classmethod
    def create_if_not_exists(cls, room):
        with cls._lock:
            if room.id not in cls._requests:
                cls._requests[room.id] = queue.Queue(maxsize=1)

            if room.id not in cls._responses:
                cls._responses[room.id] = queue.Queue(maxsize=1)

    @classmethod
    def handle(cls, event):
        room = get_or_create_room(event)
        cls.create_if_not_exists(room)

        try:
            if cls._requests[room.id].get_nowait():
                cls._responses[room.id].put(event, timeout=1)
        except queue.Empty:
            '''No request, ignore the message'''
            pass

    @classmethod
    def request(cls, room):
        cls.create_if_not_exists(room)

        cls._requests[room.id].put_nowait(True)
        return cls._responses[room.id].get(timeout=60)
