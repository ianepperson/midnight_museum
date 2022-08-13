from threading import Thread, Lock
from queue import SimpleQueue, Empty
from time import time
import logging

from effect_base import Effect as BaseEffect
from effect_test_pattern import TestPattern

log = logging.getLogger(__name__)

GLOBAL_HANDLER = None
HANDLER_LOCK = Lock()


def get_effects_handler(setup, mqtt):
    '''Get the singleton of the handler'''
    global GLOBAL_HANDLER
    if HANDLER_LOCK.acquire(timeout=0.1):
        if not GLOBAL_HANDLER:
            GLOBAL_HANDLER = EffectsHandler(setup, mqtt)

    return GLOBAL_HANDLER


class Commands:
    stop = "STOP"
    load_image = "LOAD_IMAGE"


FRAME_SECONDS = 0.2


class EffectsHandler:
    def __init__(self, setup, mqtt):
        self.mqtt = mqtt
        self.setup = setup
        self._started = Lock()
        self._commands = SimpleQueue()
        self._effects_thread = None
        self._last_frame_time = 0.0

        # Instantiate a base effect for use as a "last position"
        self._last_effect = BaseEffect()

        # lights is a dictionary of position (x, y) where each is 1-5
        # with the value being a Tasmota Light object
        self.lights = {}

        self.effect = TestPattern()
        self.step = 5
        self.level = 0

    @property
    def started(self):
        return self._started.locked()

    def start(self):
        if not self._started.acquire(blocking=False):
            log.info('Effects server already started')
            return

        if self._effects_thread is None:
            self._effects_thread = Thread(
                target=self._handle_effects,
                name='effects'
            )
        self._effects_thread.start()
        log.info('XXXX Effects server started')

    def stop(self):
        # TODO: empty the queue first?
        self._commands.put_nowait((Commands.stop, None))
        self._effects_thread.join()
        self._started.release()

    def add_light(self, position, light_id):
        self.lights[position] = self.mqtt.get_light(light_id)

    def load_image(self, image):
        self._commands.put(Commands.load_image, image)

    def _load_image(self, image):
        # TODO: handle loading the new image into memory
        pass

    def _send_pixel(self, sn, color):
        light = self.mqtt.get_light(sn)
        if not light:
            return

        light.cmd.color(color)

    def _send_frame(self):
        '''Send the next frame of the animation'''
        # Progress the animation by a step
        self.effect.next_frame()
        # Walk through any pixels that changed
        for (row, col), color in self._last_effect.get_diff(self._last_effect):
            # Look up the light assigned to that pixel
            sn = self.setup.assignment[row][col]
            # send it!
            self._send_pixel(sn, f'{color[0],color[1],color[2]}')

    # def _send_frame(self):
    #     # Bounce a variable up and down
    #     if self.level + self.step > 255:
    #         self.step = -self.step
    #         self.level = 255

    #     if self.level + self.step < 0:
    #         self.step = -self.step
    #         self.level = 0

    #     self.level += self.step

    #     sn = self.setup.assignment[0][0]
    #     self._send_pixel(sn, f'{self.level},0,0')

    def _next_frame(self) -> float:
        '''
        Runs the next frame and returns how long to wait before calling again
        '''
        # TODO: handle sending the next set of commands to the lights
        now = time()
        next_time = self._last_frame_time + FRAME_SECONDS
        # we haven't reached our time yet
        if now < next_time:
            # wait until our time has come
            return next_time - now + 0.001

        self._send_frame()

        self._last_frame_time = now
        return FRAME_SECONDS + 0.001

    def _handle_effects(self):
        wait_time = 0.1
        while True:
            try:
                # Maybe refactor? If lots of commands come in the frames will
                # be delayed. Maybe not a problem?
                (cmd, data) = self._commands.get(timeout=wait_time)
            except Empty:
                wait_time = self._next_frame()
                continue

            match cmd:
                case Commands.stop:
                    break

                case Commands.load_image:
                    self.load_image(data)
