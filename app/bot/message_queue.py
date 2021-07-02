import queue
from threading import RLock

from .utils import get_or_create_room


class RequestTimout(Exception):
    pass


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
            if not cls._requests[room.id].empty():
                cls._responses[room.id].put(event, timeout=1)
                cls._requests[room.id].get()
                return True
            return False
        except queue.Empty:
            '''No request, ignore the message'''
            return False

    @classmethod
    def request(cls, room, timeout=30):
        try:
            cls.create_if_not_exists(room)

            cls._requests[room.id].put_nowait(True)
            return cls._responses[room.id].get(timeout=timeout)

        except queue.Empty:
            MessageQueue.clear(room)
            raise RequestTimout

    @classmethod
    def available(cls, room):
        cls.create_if_not_exists(room)
        return cls._requests[room.id].empty()

    @classmethod
    def clear(cls, room):
        cls.create_if_not_exists(room)
        try:
            cls._requests[room.id].get_nowait()
        except queue.Empty:
            pass
