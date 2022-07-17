from tasmota import Light, Discover
import paho.mqtt.client as mqtt


class MQTTHandler:
    def __init__(self, host='127.0.0.1', port=1883):
        self.host = host
        self.port = port
        self._lights = {}
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.discover = Discover(self.client)
        self.discover.on_new_device = self._on_new_device

        # for creating callbacks
        self.on_connect = None
        self.on_message = None

    def publish(self, *args, **kwargs):
        self.client.publish(*args, **kwargs)

    def start(self):
        print(f'Connecting to MQTT server at {self.host}:{self.port}')
        self.client.connect(self.host, self.port)
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()

    def _on_connect(self, client, userdata, flags, rc):
        # subscribe to all channels
        print('MQTT Connected. Listening for any changes')
        client.subscribe('#')

    def _on_message(self, client, userdata, msg):
        # All status messages start with "stat/"
        # topic="stat/tasmota_197CD7/POWER1" payload="ON"

        print(f'MQTT Received {msg.topic} :: {msg.payload}')

        if not msg or not msg.topic or not msg.topic.startswith('stat/'):
            return

        if self.on_message is not None:
            self.on_message(client, userdata, msg)

        try:
            prefix, topic, command = msg.topic.split('/')
        except ValueError:
            # If we don't have the expected count of values
            return

        if not userdata:
            return

        instance = userdata.get(topic)
        if not instance:
            return

    def _on_new_device(self, device):
        print(f'new device {device.sn}')

    def get_light(self, light_id) -> Light:
        '''Get a light by its ID.

        Returns a tasmota.Light object.
        '''
        if light_id not in self._lights:
            self._lights[light_id] = Light(mqtt_client=self, topic=light_id)

        return self._lights[light_id]
