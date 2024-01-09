import datetime
import threading
import time
from flask import Flask, request
import json
import config
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import paho.mqtt.client as mqtt
from state import State
from flask_sock import Sock
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
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
    d = json.loads(msg.payload.decode('utf-8'))
    _update_device_state(d)
    save_to_db(d)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(cfg['mqtt']['host'], cfg['mqtt']['port'], 60)
client.loop_start()

# -----------------------------------------------------------------------------
# Server

state = State()
glo_ws_alarms = [] # List of websocket connections for the '/alarm' endpoint.


def _update_device_state(d: dict):
    state.update_device_state(d)


def _periodically_set_state_pir_to_false():
    """
        The PIR sensor only sends signals when it detects motion. Therefore, it
        is up to up to remove stale PIR readings after a while.
        That way, we can emulate STATE from EVENTS.

        Run this function in a background thread.
    """
    staleness_threshold_seconds = 2
    sleep_time = 1

    while True:
        now = datetime.datetime.now().timestamp()
        for device_name, device in state.device_state.items():
            if 'PIR' not in device_name:
                continue
            is_stale = (now - device['timestamp_']) > staleness_threshold_seconds 
            if is_stale:
                state.device_state[device_name]['motion'] = False

        time.sleep(sleep_time)


def _publish_alarm_to_ws(is_alarm: bool):
    glo_ws_alarms_copy = glo_ws_alarms.copy()
    for ws in glo_ws_alarms_copy:
        try:
            data = { "alarm": is_alarm }
            ws.send(json.dumps(data))
        except Exception:
            glo_ws_alarms.remove(ws)


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
        return ""
    

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
        "number_of_people": state.number_of_people,
        "device_state": state.device_state
    }


@sock.route("/ws/alarm")
def ws_alarm(ws):
    global glo_ws_alarms
    glo_ws_alarms.append(ws)

    # If a client connects AFTER the alarm has been set off, we want to let him know.
    if state.alarm:
        _publish_alarm_to_ws(state.alarm)
    
    while True:
        time.sleep(10)

    glo_ws_alarms.remove(ws)


@sock.route("/ws/state")
def ws_state(ws):
    while True:
        d = {
            "alarm": state.alarm,
            "number_of_people": state.number_of_people,
            "device_state": state.device_state
        }
        ws.send(json.dumps(d))
        time.sleep(1)


if __name__ == '__main__':
    t = threading.Thread(target=_periodically_set_state_pir_to_false, daemon=True)
    t.start()

    app.run(debug=True, use_reloader=False) # , host="10.1.121.29"