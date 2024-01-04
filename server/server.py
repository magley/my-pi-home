import time
from flask import Flask, request
import json
import config
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import paho.mqtt.client as mqtt
from state import State
from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)
cfg = config.load_config("config.json", "influx_token.secret")


# -----------------------------------------------------------------------------
# InfluxDB

influx = InfluxDBClient(url=cfg['influxdb']['url'], token=cfg['influxdb']['token'], org=cfg['influxdb']['org'])

def save_to_db(item: dict):
    try:
        write_api = influx.write_api(write_options=SYNCHRONOUS)
        point = (
            Point(item["measurement"])
                .tag("simulated", item["simulated"])
                .tag("runs_on", item["runs_on"])
                .tag("name", item["name"])
                .field("measurement", item["value"])
        )

        write_api.write(bucket=cfg['influxdb']['bucket'], org=cfg['influxdb']['org'], record=point)
    except Exception:
        print("Error")

# -----------------------------------------------------------------------------
# MQTT

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("iot/dht")
    client.subscribe("iot/pir")
    client.subscribe("iot/uds")
    client.subscribe("iot/mds")
    client.subscribe("iot/mbkp")
    client.subscribe("iot/buzzer")
    client.subscribe("iot/led")
    client.subscribe("iot/lcd")
    client.subscribe("iot/gyro")

def on_message(client, userdata, msg):
    save_to_db(json.loads(msg.payload.decode('utf-8')))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(cfg['mqtt']['host'], cfg['mqtt']['port'], 60)
client.loop_start()

# -----------------------------------------------------------------------------
# Server

state = State()
glo_ws_alarms = [] # List of websocket connections for the '/alarm' endpoint.


def _publish_alarm_to_ws(is_alarm: bool):
    for ws in glo_ws_alarms:    
        data = { "alarm": is_alarm }
        ws.send(json.dumps(data))


def _set_alarm(is_alarm: bool):
    """
    Set the alarm to True, publish through websocket, send value to InfluxDB.
    """

    state.set_alarm(is_alarm)
    _publish_alarm_to_ws(is_alarm)

    # Write to influxDB.
    try:
        write_api = influx.write_api(write_options=SYNCHRONOUS)
        point = (
            Point("alarm").field("is_alarm", int(state.alarm)) # Influxdb REQUIRES AT LEAST 1 FIELD!
        )
        write_api.write(bucket=cfg['influxdb']['bucket'], org=cfg['influxdb']['org'], record=point)

    except Exception:
        print("Error")


@app.route("/people", methods = ['GET', 'POST'])
def people():
    if request.method == 'GET':
        return {
            "number_of_people": state.number_of_people
        }
    elif request.method == 'POST':
        entering = request.json['entering']
        if entering:
            state.person_enter()
        else:
            state.person_exit()

        return ""


@app.route("/alarm", methods = ['GET', 'POST'])
def alarm():
    if request.method == 'GET':
        return { "alarm": state.alarm }
    elif request.method == 'POST':
        is_alarm = request.json['alarm']
        if state.alarm != is_alarm:
            _set_alarm(is_alarm)
    

@app.route("/rpir", methods = ['POST'])
def on_rpir_motion_detected():
    if request.method == 'POST':
        if state.number_of_people == 0 and not state.alarm:
            _set_alarm(True)
        return ""


@app.route("/state")
def get_state():
    return {
        "alarm": state.alarm,
        "number_of_people": state.number_of_people
    }


@sock.route("/ws/alarm")
def ws_alarm(ws):
    global glo_ws_alarms
    glo_ws_alarms.append(ws)

    # If a client connects AFTER the alarm has been set off, we want to let him know.
    if state.alarm:
        _publish_alarm_to_ws(state.alarm)
    
    while True:
        time.sleep(10) # Keep the connection alive.


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False) # , host="10.1.121.29"