from queue import SimpleQueue


class Commands:
    stop = "STOP"
    load_image = "LOAD_IMAGE"


class EffectsHandler:
    def __init__(self, mqtt, commands: SimpleQueue):
        self.mqtt = mqtt
        self.commands = commands

        # lights is a dictionary of position (x, y) where each is 1-5
        # with the value being a Tasmota Light object
        self.lights = {}

    def start(self):
        pass

    def stop(self):
        # todo: empty the queue first
        self.commands.put_nowait((Commands.stop, None))

    def add_light(self, position, light_id):
        self.lights[position] = self.mqtt.get_light(light_id)

    def load_image(self, image):
        self.commands.put(Commands.load_image, image)

    def _load_image(self, image):
        pass

    def _handle_commands(self):
        while True:
            (cmd, data) = self.commands.get()
            match cmd:
                case Commands.stop:
                    break

                case Commands.load_image:
                    self.load_image(data)
