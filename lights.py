import logging
from asyncio import create_task, sleep, Queue, CancelledError

from aioesphomeapi import APIClient

from setup import GRID_SIZE

log = logging.getLogger(__name__)


# IP_PREFIX = '192.168.9.1'  # 192.168.9.101 - 125

LIGHTS = None


def get_lights(setup):
    global LIGHTS
    if not LIGHTS:
        LIGHTS = Lights(setup)
    return LIGHTS


class Light:
    def __init__(self, host):
        self.host = host
        self.state = 'Initialized'
        self._command_queue = Queue(maxsize=1)
        self._change_handler = None
        self._service_calls_handler = None

    def __repr__(self):
        return f'<Light(host="{self.host}")>'

    def start(self):
        self.state = 'Running'
        self._connection_manager = create_task(self._run())

    def stop(self):
        self.state = 'Stopped'
        if self._change_handler:
            self._change_handler.cancel()
        if self._service_calls_handler:
            self._service_calls_handler.cancel()
        if self._connection_manager:
            self._connection_manager.cancel()

    def _spawn_handlers(self):
        self._change_handler = create_task(
            self.client.subscribe_states(self._change_callback)
        )
        self._service_calls_handler = create_task(
            self.client.subscribe_service_calls(self._service_calls_callback)
        )

    async def get_key(self):
        sensors, services = await self.client.list_entities_services()
        for sensor in sensors:
            if sensor.object_id == 'kauf_bulb':
                log.debug(f'{self.host} using {sensor=}')
                return sensor.key

        # key = 2723974766
        log.error(f'{self.host} UNABLE TO FIND A GOOD KEY. Trying default')
        return 2723974766

    async def _run(self):
        if not self.host:
            # If there's actually no host to connect to, just perform NOOP
            return

        while True:
            self._change_handler = None
            self.client = APIClient(self.host, 6053, None)
            try:
                await self.client.connect(login=True)
            except CancelledError:
                log.info(f'{self.host} Exiting connection manager')
                return
            except KeyboardInterrupt:
                return
            except Exception as e:
                log.error(f'Could not connect to {self.host}: {e!r}')
                self.state = f'Connection error {e!r}'
                sleep(10)
                continue

            self._spawn_handlers()
            key = await self.get_key()

            self.state = 'Running'

            try:
                while True:
                    # Pass along all commands to the client
                    cmd = await self._command_queue.get()
                    log.debug(f'{self.host} :: sending light_command({cmd})')
                    await self.client.light_command(key=key, **cmd)
            except CancelledError:
                log.info(f'{self.host} Exiting connection manager')
                return
            except KeyboardInterrupt:
                return
            except Exception as e:
                log.error(f'{self.host} Error while sending. {e!r}')
                self.state = f'Transmission error {e!r}'
                log.debug(f'{self.host} pausing for 10 seconds to reconnect')
                sleep(10)
            finally:
                await self.client.disconnect()

    def _change_callback(self, state):
        '''Device changes'''
        log.debug(f'{self.host} [change] :: {state}')

    def _service_calls_callback(self, state):
        '''Service state changes'''
        log.debug(f'{self.host} [service calll] :: {state}')

    def command(self, **cmd):
        '''
        state: Optional[bool] = None,
        brightness: Optional[float] = None,
        color_mode: Optional[int] = None,
        color_brightness: Optional[float] = None,
        rgb: Optional[Tuple[float, float, float]] = None,
        white: Optional[float] = None,
        color_temperature: Optional[float] = None,
        cold_white: Optional[float] = None,
        warm_white: Optional[float] = None,
        transition_length: Optional[float] = None,
        flash_length: Optional[float] = None,
        effect: Optional[str] = None,
        '''
        # We're only interested in the latest command
        if self._command_queue.full():
            # If the queue is full (not connected) just clear it out
            self._command_queue.get_nowait()

        cmd.setdefault('state', True)

        if cmd.get('rgb') == (0, 0, 0):
            cmd['state'] = False

        rgb = cmd.get('rgb')
        if rgb:
            brightness = cmd.get('color_brightness', 1.0) * max(rgb)
            if brightness < 0.1:
                cmd['state'] = False
            else:
                cmd['color_brightness'] = brightness

        log.debug(f'{self.host} :: queueing command {cmd}')
        self._command_queue.put_nowait(cmd)


class Lights:
    '''Container for all the lights.'''
    def __init__(self, setup):
        self.setup = setup
        self._handlers = []
        self._handler_by_host = {}
        self.setup_handlers()

    def setup_handlers(self):
        offset = 0
        self._handlers = []
        # Generate a 5x5 grid
        for row_num in range(GRID_SIZE):
            row = []
            self._handlers.append(row)

            for col_num in range(GRID_SIZE):
                offset += 1
                host = self.setup.assignment[row_num][col_num]
                light = self._handler_by_host.get(host)
                if not light:
                    if host:
                        log.info(f'Setting up a handler for "{host}"')
                    light = Light(host)
                    self._handler_by_host[host] = light

                row.append(light)

    @property
    def handlers(self):
        handlers = self._handler_by_host.copy()
        try:
            del handlers[None]
        except KeyError:
            pass
        return handlers

    def __getitem__(self, row: int):
        return self._handlers[row]

    def __repr__(self):
        return self._handlers.__repr__()

    def start(self):
        for row in self._handlers:
            for light in row:
                light.start()

    def stop(self):
        for row in self._handlers:
            for light in row:
                light.stop()
