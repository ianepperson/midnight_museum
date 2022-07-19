from os.path import exists
from threading import Lock
import json


GRID_SIZE = 5  # 5x5 grid of lights


class Setup:
    def __init__(self, filename):
        self._filename = filename
        self._lock = Lock()

        # Defaults
        self.assignment = []
        for _ in range(GRID_SIZE):
            self.assignment.append([None] * GRID_SIZE)

        self.effects_image = None
        self.mqtt_host = '127.0.0.1'
        self.mqtt_port = 1883

        # Load the file over the defaults

        self._load()

    def _load(self):
        '''Load everything from the filename that isn't prefixed with _'''
        if not exists(self._filename):
            return

        self._lock.acquire(timeout=5)
        try:
            with open(self._filename, 'r') as f:
                data = json.load(f)

            for key, value in data.items():
                if not key.startswith('_'):
                    setattr(self, key, value)
        finally:
            self._lock.release()

    def save(self):
        '''Save everything to the filename that isn't prefixed with _'''
        data = {
            key: value for key, value in self.__dict__.items()
            if not key.startswith('_')
        }
        self._lock.acquire(timeout=5)
        try:
            with open(self._filename, 'w') as f:
                json.dump(data, f)
        finally:
            self._lock.release()
