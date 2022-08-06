from flask import Flask, g, render_template, request
# , redirect, url_for

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/devices')
def devices():
    return render_template('devices.html')


@app.route('/mqtt_setting', methods=['POST', 'GET'])
def mqtt_setting():
    if request.method == 'POST':
        host = request.form.get('host')
        port = request.form.get('port')

        host = host or g.setup.mqtt_host
        port = port or g.setup.mqtt_port
        if host != g.setup.mqtt_host or port != g.setup.mqtt_port:
            g.mqtt.update_connection_settings(host, port)

    return render_template('mqtt_setting.html')


@app.route('/lanterns', methods=['POST', 'GET'])
def lanterns():
    if request.method == 'POST':
        changed = False
        for row_num, row in enumerate(g.mqtt.setup.assignment[:]):
            for col_num, topic in enumerate(row[:]):
                new_topic = request.form.get(f'topic_{row_num}_{col_num}')
                if new_topic.lower() == 'none':
                    new_topic = None

                if topic != new_topic:
                    g.mqtt.setup.assignment[row_num][col_num] = new_topic
                    changed = True
        if changed:
            g.mqtt.setup.save()

    # Jinja2 requires tricks for a nested list. Easier to just flatten it
    # flat_lantern_topics = []
    # for topic_row in g.mqtt.setup.assignment:
    #     flat_lantern_topics += topic_row

    # Hydrate the flat list of lanterns for the template
    # flat_lanterns = [
    #     g.mqtt.discover.devices.get(topic)
    #     for topic in flat_lantern_topics
    # ]

    # lantern_row_len = len(g.mqtt.setup.assignment)

    return render_template('lanterns.html')
