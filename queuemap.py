import time
from collections import defaultdict
from setup_logger import logger

class QueueMap(object):

    def __init__(self, window):
        self._store = defaultdict(list)
        self.window = window

    def get_queue(self, name):
        return self._store.get(name, [])

    def pop(self, name):
        queue = self.get_queue(name)
        if queue:
            msg = queue.pop()
            return msg
        return None

    def set(self, name, message):
        self._store[name].insert(0, message)
        #logger.info(self._store[name])

    def check_window(self):
        vals = self._store.values()
        if all(len(item) == self.window for item in vals):
            logger.info('ok')