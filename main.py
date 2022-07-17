from argparse import ArgumentParser
from time import sleep
import logging

from mqtt import MQTTHandler
from effects import EffectsHandler


logging.basicConfig(level=logging.DEBUG)


def go(mqtt_host, mqtt_port):
    print('Starting MQTT handler...')
    mqtt = MQTTHandler(host=mqtt_host, port=mqtt_port)
    mqtt.start()
    print('Starting effects handler...')
    effects_handler = EffectsHandler(mqtt)
    effects_handler.start()
    print('------------------------------')
    print('Running. Press ctrl-C to halt.')
    print('------------------------------')
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print(' Shutdown requested')
    finally:
        print('Halting effects handler...')
        effects_handler.stop()
        print('Halting MQTT handler...')
        mqtt.stop()
    print('Done.')


if __name__ == '__main__':
    # Initialize parser
    parser = ArgumentParser()
    parser.add_argument(
        '--mqtt_host',
        metavar='HOST',
        help='MQTT host to connect to',
        default='127.0.0.1'
    )
    parser.add_argument(
        '--mqtt_port',
        metavar='PORT',
        help='MQTT port to connect to',
        type=int,
        default=1883
    )

    # Grab the arguments
    args = parser.parse_args()
    # Run with it
    go(args.mqtt_host, args.mqtt_port)
