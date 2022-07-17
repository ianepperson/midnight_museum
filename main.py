from argparse import ArgumentParser
# from time import sleep
import logging

import flask

from mqtt import MQTTHandler
from effects import EffectsHandler
from web_server import app


logging.basicConfig(level=logging.DEBUG)


def go(mqtt_host, mqtt_port, http_server_port):
    print('Starting MQTT handler...')
    mqtt = MQTTHandler(host=mqtt_host, port=mqtt_port)
    mqtt.start()
    print('Starting effects handler...')
    effects_handler = EffectsHandler(mqtt)
    effects_handler.start()

    @app.before_request
    def load_controls():
        flask.g.mqtt = mqtt
        flask.g.effects = effects_handler

    print('------------------------------')
    print('Running. Press ctrl-C to halt.')
    print('------------------------------')
    try:
        app.run(debug=True, port=http_server_port)
        # while True:
        #     sleep(1)
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
        '--http_server_port',
        metavar='PORT',
        help='The port the web interface is served on',
        type=int,
        default=8080
    )
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
    go(args.mqtt_host, args.mqtt_port, args.http_server_port)
