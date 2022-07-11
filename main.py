from time import Sleep

from mqtt import MQTTHandler
from effects import EffectsHandler


def go():
    mqtt = MQTTHandler()
    mqtt.start()
    effects_handler = EffectsHandler(mqtt)
    effects_handler.start()
    try:
        while True:
            Sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        effects_handler.stop()
        mqtt.stop()
