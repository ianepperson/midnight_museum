from threading import Lock
import logging

from tasmota import Light, Discover
import paho.mqtt.client as mqtt

log = logging.getLogger(__name__)

GLOBAL_HANDLER = None
HANDLER_LOCK = Lock()


def get_mqtt_handler(setup):
    '''Get the singleton of the handler'''
    global GLOBAL_HANDLER
    if HANDLER_LOCK.acquire(timeout=0.1):
        if not GLOBAL_HANDLER:
            GLOBAL_HANDLER = MQTTHandler(setup)

    return GLOBAL_HANDLER


class MQTTHandler:
    def __init__(self, setup):
        self.setup = setup
        self._lights = {}
        self._started = Lock()
        self._userdata = None

        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.discover = Discover(self.client)
        self.discover.on_new_device = self._on_new_device

        # for creating callbacks
        self.on_connect = None
        self.on_message = None

        self.status = 'Disconnected'

    def user_data_set(self, value):
        self._userdata = value

    @property
    def started(self):
        return self._started.locked()

    @property
    def host(self):
        return self.setup.mqtt_host

    @property
    def port(self):
        return self.setup.mqtt_port

    def update_connection_settings(self, host, port):
        log.info(f'Updating connection settings to {host=} {port=}')
        self.setup.mqtt_host = host
        self.setup.mqtt_port = port
        self.setup.save()
        self.restart()

    def publish(self, *args, **kwargs):
        self.client.publish(*args, **kwargs)

    def start(self):
        if not self._started.acquire(blocking=False):
            log.info('MQTT server already started')
            return

        log.info(f'Connecting to MQTT server at {self.host}:{self.port}')
        self.status = 'Connecting...'
        try:
            self.client.connect(self.host, self.port)
        except Exception as e:
            self.status = e
        else:
            self.client.loop_start()

    def restart(self):
        log.info(f'Restarting MQTT connection')
        self.status = 'Restarting...'
        self.client.disconnect()
        self.status = 'Disconnected, reconnecting...'
        self._started.release()
        self.start()

    def stop(self):
        self.client.loop_stop()
        self._started.release()

    def _on_connect(self, client, userdata, flags, rc):
        # subscribe to all channels
        log.info('MQTT Connected. Listening for any changes')
        self.status = 'Connected'
        client.subscribe('#')

    def _on_message(self, client, userdata, msg):
        # All status messages start with "stat/"
        # topic="stat/tasmota_197CD7/POWER1" payload="ON"

        log.debug(f'MQTT Received {msg.topic} :: {msg.payload}')

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
        log.info(f'new device {device.sn}')

    def get_light(self, light_id) -> Light:
        '''Get a light by its ID.

        Returns a tasmota.Light object.
        '''
        if not light_id:
            return None

        device = self.discover.devices.get(light_id)

        if not device:
            return None

        # device.topic
        if light_id not in self._lights:
            self._lights[light_id] = Light(
                mqtt_client=self, topic=device.topic
            )

        return self._lights[light_id]
