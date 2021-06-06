from queue import Queue
from threading import Lock


class MessageQueue:
    def __init__(self):
        self._queue = {}
        self._lock = Lock()

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
