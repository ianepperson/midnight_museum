from argparse import ArgumentParser
import logging

import quart

# from mqtt import get_mqtt_handler
from lights import get_lights
from effects import get_effects_handler
from setup import Setup
from web_server import app


logging.basicConfig(level=logging.DEBUG)


def create_app():
    lights_handler = get_lights(setup)

    effects_handler = get_effects_handler(setup, lights_handler)

    @app.before_serving
    async def startup():
        print('Starting lights communication...')
        lights_handler.start()
        print('Starting effects handler...')
        effects_handler.start()

    @app.before_request
    def load_controls():
        quart.g.lights = lights_handler
        quart.g.effects = effects_handler
        quart.g.setup = setup

    @app.before_websocket
    def load_ws_controls():
        quart.g.lights = lights_handler
        quart.g.effects = effects_handler
        quart.g.setup = setup

    return app


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
    parser.add_argument(
        '--profile',
        metavar='FILENAME',
        help='Run with the profiler and dump to file',
        default=None
    )

    # Grab the arguments
    args = parser.parse_args()
    # Create the setup file
    setup = Setup(args.setup)
    # Run with it
    # go(setup, args.http_server_port)

    app_ = create_app()

    if not args.profile:
        app_.run(port=args.http_server_port, host='0.0.0.0')

    if args.profile:
        import cProfile
        import pstats

        with cProfile.Profile() as pr:
            app_.run(port=args.http_server_port, host='0.0.0.0')

        stats = pstats.Stats(pr)
        stats.sort_stats(pstats.SortKey.TIME)
        if args.profile == 'stdout':
            stats.print_stats()
        else:
            stats.dump_stats(filename=args.profile)
