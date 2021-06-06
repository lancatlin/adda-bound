import queue
from threading import Lock

from .utils import with_room


class MessageQueue:
    def __init__(self):
        self._queue = {}
        self._lock = Lock()
        self._requests = {}
        self._responses = {}

    def create_if_not_exists(self, room):
        if room.id not in self._requests:
            self._requests[room.id] = queue.Queue(maxsize=1)

        if room.id not in self._responses:
            self._responses[room.id] = queue.Queue(maxsize=1)

    def handle(self, event):
        @with_room
        def func(event, room):
            self.create_if_not_exists(room)
            if self._requests[room.id].get_nowait():
                self._responses[room.id].put(event.message.text)

        try:
            func(event)
        except queue.Empty:
            '''No request, ignore the message'''
            pass

    def request(self, room):
        self.create_if_not_exists(room)

        self._requests[room.id].put_nowait(True)
        return self._responses[room.id].get(timeout=180)

    def with_lock(callback):
        def func(self, *arg, **kwargs):
            try:
                self._lock.acquire(blocking=True, timeout=5)
                return callback(self, *arg, **kwargs)
            finally:
                self._lock.release()
        return func

    @with_lock
    def set(self, key, value):
        self._queue[key] = value

    @with_lock
    def get(self, key):
        return self._queue[key]

    @with_lock
    def delete(self, key):
        del self._queue[key]

    @with_lock
    def contain(self, key):
        return key in self._queue
