from threading import Thread
from queue import SimpleQueue, Empty
from time import time


class Commands:
    stop = "STOP"
    load_image = "LOAD_IMAGE"


FRAME_SECONDS = 0.2


class EffectsHandler:
    def __init__(self, mqtt):
        self.mqtt = mqtt
        self._commands = SimpleQueue()
        self._effects_thread = None
        self._last_frame_time = 0.0

        # lights is a dictionary of position (x, y) where each is 1-5
        # with the value being a Tasmota Light object
        self.lights = {}

    def start(self):
        if self._effects_thread is None:
            self._effects_thread = Thread(
                target=self._handle_effects,
                name='effects'
            )
        self._effects_thread.start()

    def stop(self):
        # TODO: empty the queue first?
        self._commands.put_nowait((Commands.stop, None))
        self._effects_thread.join()

    def add_light(self, position, light_id):
        self.lights[position] = self.mqtt.get_light(light_id)

    def load_image(self, image):
        self._commands.put(Commands.load_image, image)

    def _load_image(self, image):
        # TODO: handle loading the new image into memory
        pass

    def _send_frame(self):
        pass

    def _next_frame(self):
        # TODO: handle sending the next set of commands to the lights
        now = time()
        if self._last_frame_time + FRAME_SECONDS < now:
            return now - self._last_frame_time + FRAME_SECONDS + 0.001

        self._send_frame()

        self._last_frame_time = now
        return now + FRAME_SECONDS + 0.001

    def _handle_effects(self):
        wait_time = 0.01
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
