from asyncio import create_task, sleep, CancelledError, Queue, QueueFull
from threading import Lock
from time import time
import logging
import traceback

from effect_base import Effect as BaseEffect
from effect_test_pattern import TestPattern
from effect_lighthouse import LighthousePattern
from effect_diagonal_hue import DiagonalHuePattern
from effect_ripple import RipplePattern
from effect_party import PartyPattern

log = logging.getLogger(__name__)

GLOBAL_HANDLER = None
HANDLER_LOCK = Lock()


def get_effects_handler(setup, lights):
    '''Get the singleton of the handler'''
    global GLOBAL_HANDLER
    if HANDLER_LOCK.acquire(timeout=0.1):
        if not GLOBAL_HANDLER:
            GLOBAL_HANDLER = EffectsHandler(setup, lights)

    return GLOBAL_HANDLER


class Commands:
    stop = "STOP"
    load_image = "LOAD_IMAGE"


FRAME_SECONDS = 0.4


class EffectsHandler:
    def __init__(self, setup, lights):
        self.lights = lights
        self.setup = setup
        self._started = False
        self._effects_thread = None
        self._change_queues = []
        self._last_frame_time = 0.0

        # Instantiate a base effect for use as a "last position"
        self._last_effect = BaseEffect()

        self.effect = RipplePattern()
        self.level = 1.0

    @property
    def started(self):
        return self._started

    def start(self):
        if self.started:
            log.info('Effects server already started')
            return

        self._effects_thread = create_task(self._handle_effects())
        self._started = True
        log.info('Effects server started')

    def stop(self):
        if self._effects_thread:
            self._effects_thread.cancel()
        self._started = False

    def get_change_queue(self) -> Queue:
        '''Get a queue that sends all light changes as events.'''
        # 5x5 grid, 2 frames max = 50
        # If the queue overflows, it's automatically culled
        changes = Queue(maxsize=100)
        self._change_queues.append(changes)
        return changes

    def _send_to_change_queues(self, **message):
        for changes in self._change_queues[:]:
            try:
                changes.put_nowait(message)
            except QueueFull:
                self._change_queues.remove(changes)
                changes.get_nowait()
                changes.put_nowait('closed')
                log.info('Removing full queue')

    def _send_frame(self):
        '''Send the next frame of the animation'''
        # Progress the animation by a step
        self.effect.next_frame()
        log.debug(f'effect step now at {self.effect.step}')
        # Walk through any pixels that changed
        for (row, col), color in self._last_effect.get_diff(self.effect):
            log.debug(f'changed {col=} {row=} {color=}')
            transition_length = self.effect.transition_length[row][col]
            # This might be reworked to use the same call
            self.lights[row][col].command(
                rgb=color,
                color_brightness=self.level,
                transition_length=transition_length,
            )
            self._send_to_change_queues(
                position=(row, col),
                rgb=color,
                brightness=self.level,
                transition_length=transition_length,
            )

    def _next_frame(self) -> float:
        """
        Runs the next frame and returns how long to wait before calling again
        """
        now = time()
        next_time = self._last_frame_time + FRAME_SECONDS
        # we haven't reached our time yet
        if now < next_time:
            # wait until our time has come
            return next_time - now + 0.001

        self._send_frame()

        self._last_frame_time = now
        return FRAME_SECONDS + 0.001

    async def _handle_effects(self):
        log.info('Effects handler running')
        wait_time = 1
        while True:
            try:
                wait_time = self._next_frame()
            except CancelledError:
                return
            except Exception as e:
                log.error(f'While getting next frame: {e!r}')

                traceback.print_exc()

            await sleep(wait_time)
