# import aioesphomeapi
import asyncio

from lights import get_lights
from setup import Setup


setup = Setup('setup.json')


async def main():
    lights = get_lights(setup)
    lights.start()

    run_ = True
    sleep_time = 3
    while run_:
        await asyncio.sleep(sleep_time)
        # breakpoint()


# async def main():
#     """Connect to an ESPHome device and wait for state changes."""
#     cli = aioesphomeapi.APIClient('192.168.9.4', 6053, None)

#     await cli.connect(login=True)

#     def change_callback(state):
#         """Print the state changes of the device.."""
#         print(state)

#     # Subscribe to the state changes
#     await cli.subscribe_states(change_callback)


loop = asyncio.get_event_loop()
try:
    asyncio.ensure_future(main())
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    loop.close()
