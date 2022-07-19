from argparse import ArgumentParser
import logging

import flask

from mqtt import MQTTHandler
from effects import EffectsHandler
from setup import Setup
from web_server import app


logging.basicConfig(level=logging.DEBUG)


def go(setup_file, http_server_port):
    setup = Setup(setup_file)
    print('Starting MQTT handler...')
    mqtt = MQTTHandler(setup)
    mqtt.start()
    print('Starting effects handler...')
    effects_handler = EffectsHandler(setup, mqtt)
    effects_handler.start()

    @app.before_request
    def load_controls():
        flask.g.mqtt = mqtt
        flask.g.effects = effects_handler
        flask.g.setup = setup

    print('------------------------------')
    print('Running. Press ctrl-C to halt.')
    print('------------------------------')
    try:
        app.run(debug=True, port=http_server_port)
    except KeyboardInterrupt:
        print(' Shutdown requested')
    finally:
        print('Halting effects handler...')
        effects_handler.stop()
        print('Halting MQTT handler...')
        mqtt.stop()

    print(f'Saving the setup to {setup_file}')
    setup.save()

    print('Done.')


if __name__ == '__main__':
    # Initialize parser
    parser = ArgumentParser()
    parser.add_argument(
        '--setup',
        metavar='FILENAME',
        help='The JSON file to read/store configuration.',
        default='setup.json'
    )
    parser.add_argument(
        '--http_server_port',
        metavar='PORT',
        help='The port the web interface is served on',
        type=int,
        default=8080
    )

    # Grab the arguments
    args = parser.parse_args()
    # Run with it
    go(args.setup, args.http_server_port)
