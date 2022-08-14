# import aioesphomeapi
import asyncio

from lights import get_lights
from setup import Setup


setup = Setup('setup.json')


async def main():
    lights = get_lights(setup)
    lights.start()

    run_ = True
    sleep_time = 5
    while run_:
        await asyncio.sleep(sleep_time)
        # breakpoint()
        lights[0][0].command(rgb=(1.0, 0, 0.5), brightness=0.5)
        lights[0][1].command(rgb=(0, 1.0, 0), brightness=0.5)
        # sensors, services = await client.list_entities_services()
        # print(f'{sensors=}, {services=}')

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
