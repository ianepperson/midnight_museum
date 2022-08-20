from os.path import exists
from threading import Lock
import logging
import json


log = logging.getLogger(__name__)

GRID_SIZE = 5  # 5x5 grid of lights


class Setup:
    _singletons = {}

    @classmethod
    def __call__(cls, filename):
        return cls._singltons.setdefault(filename, super()(filename))

    def __init__(self, filename):
        self._filename = filename
        self._lock = Lock()

        # Defaults
        self.assignment = []
        for _ in range(GRID_SIZE):
            self.assignment.append([None] * GRID_SIZE)

        self.effects_image = None
        self.effect_run_seconds = 300  # 5 minutes default
        self.effect_run_seconds = 10  # for testing

        # Load the file over the defaults

        self._load()

    def _load(self):
        '''Load everything from the filename that isn't prefixed with _'''
        if not exists(self._filename):
            return

        log.info(f'Loading the config from {self._filename}...')
        self._lock.acquire(timeout=5)
        try:
            with open(self._filename, 'r') as f:
                data = json.load(f)

            for key, value in data.items():
                if not key.startswith('_'):
                    setattr(self, key, value)
        except Exception:
            log.exception('Error reading config')
        else:
            log.info('Loaded.')
        finally:
            self._lock.release()

    def save(self):
        '''Save everything to the filename that isn't prefixed with _'''
        data = {
            key: value for key, value in self.__dict__.items()
            if not key.startswith('_')
        }
        log.info(f'Saving the config to {self._filename}...')
        log.debug(f'Data to save {data=}')
        self._lock.acquire(timeout=5)
        try:
            with open(self._filename, 'w') as f:
                json.dump(data, f)
                f.write('\n\n')
                f.flush()
        except Exception:
            log.exception('Error writing config')
        else:
            log.info('Saved.')
        finally:
            self._lock.release()
