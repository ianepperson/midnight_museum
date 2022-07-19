from tasmota import Light, Discover
import paho.mqtt.client as mqtt


class MQTTHandler:
    def __init__(self, setup):
        self.setup = setup
        self._lights = {}

        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.discover = Discover(self.client)
        self.discover.on_new_device = self._on_new_device

        # for creating callbacks
        self.on_connect = None
        self.on_message = None

        self.status = 'Disconnected'

    @property
    def host(self):
        return self.setup.mqtt_host

    @property
    def port(self):
        return self.setup.mqtt_port

    def update_connection_settings(self, host, port):
        print(f'Updating connection settings')
        self.setup.mqtt_host = host
        self.setup.mqtt_port = port
        self.setup.save()
        self.restart()

    def publish(self, *args, **kwargs):
        self.client.publish(*args, **kwargs)

    def start(self):
        print(f'Connecting to MQTT server at {self.host}:{self.port}')
        self.status = 'Connecting...'
        try:
            self.client.connect(self.host, self.port)
        except Exception as e:
            self.status = e
        else:
            self.client.loop_start()

    def restart(self):
        print(f'Restarting MQTT connection')
        self.status = 'Restarting...'
        self.client.disconnect()
        self.status = 'Disconnected, reconnecting...'
        self.start()

    def stop(self):
        self.client.loop_stop()

    def _on_connect(self, client, userdata, flags, rc):
        # subscribe to all channels
        print('MQTT Connected. Listening for any changes')
        self.status = 'Connected'
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
