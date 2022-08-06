from argparse import ArgumentParser
import logging

import flask

from mqtt import get_mqtt_handler
from effects import get_effects_handler
from setup import Setup
from web_server import app


logging.basicConfig(level=logging.DEBUG)


def create_app():
    print('Starting MQTT handler...')
    mqtt = get_mqtt_handler(setup)
    mqtt.start()
    print('Starting effects handler...')
    effects_handler = get_effects_handler(setup, mqtt)
    effects_handler.start()

    @app.before_request
    def load_controls():
        flask.g.mqtt = mqtt
        flask.g.effects = effects_handler
        flask.g.setup = setup

    return app


def go(setup, http_server_port):
    print('Starting MQTT handler...')
    mqtt = get_mqtt_handler(setup)
    mqtt.start()
    print('Starting effects handler...')
    effects_handler = get_effects_handler(setup, mqtt)
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

    # print(f'Saving the setup to {setup_file}')
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
    # Create the setup file
    setup = Setup(args.setup)
    # Run with it
    # go(setup, args.http_server_port)

    app_ = create_app()
    app_.run(debug=True, port=args.http_server_port)
