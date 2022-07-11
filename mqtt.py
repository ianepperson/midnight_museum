from tasmota import Light
import paho.mqtt.client as mqtt


class MQTTHandler:
    def __init__(self, host='127.0.0.1', port=1883, halt_semaphore=None):
        self.host = host
        self.port = port
        self._lights = {}
        self.client = mqtt.Client()

    def publish(self, *args, **kwargs):
        self.client.publish(*args, **kwargs)

    def start(self):
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()

    def get_light(self, light_id) -> Light:
        if light_id not in self._lights:
            self._lights[light_id] = Light(mqtt_client=self, topic=light_id)

        return self._lights[light_id]
