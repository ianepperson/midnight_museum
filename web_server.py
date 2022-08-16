import json
import logging
from quart import Quart, g, render_template, request, websocket

# , redirect, url_for

app = Quart(__name__)

log = logging.getLogger(__name__)


@app.route('/')
async def home():
    return await render_template('index.html')


@app.route('/devices')
async def devices():
    return await render_template('devices.html')


@app.route('/lanterns', methods=['POST', 'GET'])
async def lanterns():
    if request.method.upper() == 'POST':
        changed = False
        for row_num, row in enumerate(g.setup.assignment[:]):
            for col_num, host in enumerate(row[:]):
                form = await request.form
                new_host = form.get(f'host_{row_num}_{col_num}')
                if new_host.lower() == 'none' or not new_host:
                    new_host = None

                log.debug(f'  {row_num=} {col_num=} {host=} {new_host=}')
                if host != new_host:
                    g.setup.assignment[row_num][col_num] = new_host
                    changed = True
        if changed:
            g.setup.save()
            g.lights.setup_handlers()

    return await render_template('lanterns.html')


@app.route('/live_state')
async def live_state():
    return await render_template('live_state.html')


@app.websocket('/ws')
async def ws():
    await websocket.accept()
    fx_changes = g.effects.get_change_queue()
    await websocket.send(json.dumps(['started', None]))
    await websocket.send(json.dumps(['light info', g.lights.info]))
    while True:
        message = await fx_changes.get()
        await websocket.send(json.dumps(['light change', message]))
        # We'll get a single 'closed' message if the changes queue fills
        # which might happen if the connection is too slow.
        if message == 'closed':
            await websocket.close(1000)
            return
