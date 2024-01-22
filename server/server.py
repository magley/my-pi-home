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
    client.subscribe("iot/d4s7")
    client.subscribe("iot/rgb")

def on_message(client, userdata, msg):
    d = json.loads(msg.payload.decode('utf-8'))
    _update_device_state(d)
    update_security_state(d)
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
glo_ws_wakeup = [] # List of websocket connections for the '/wakeup' endpoint.


def _update_device_state(d: dict):
    state.update_device_state(d)


# [4]
def update_security_state(d: dict):
    """
    Security state starts as False, first correct PIN entry activates it.
    After that, correctly entering the PIN deactivates the alarm.
    """
    if d['name'] != 'DMS':
        return
    keys = d['value']
    for key in keys:
        state.append_dms_last_4(key)
    if state.dms_last_4.circular_equal(state.pin):
        if state.security_active:
            _set_alarm(False, '')
            # state.set_security_active(False)
        else:
            state.set_security_active(True)


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
            if 'PIR' not in device_name and device_name != 'BIR':
                continue
            is_stale = (now - device['timestamp_']) > staleness_threshold_seconds 
            if is_stale:
                state.device_state[device_name]['motion'] = False

        time.sleep(sleep_time)


def _publish_alarm_to_ws(is_alarm: bool, alarm_reason: str):
    glo_ws_alarms_copy = glo_ws_alarms.copy()
    for ws in glo_ws_alarms_copy:
        try:
            data = { "alarm": is_alarm, "alarm_reason": alarm_reason }
            ws.send(json.dumps(data))
        except Exception:
            glo_ws_alarms.remove(ws)


def _publish_wakeup_to_ws(wakeup: str):
    glo_ws_wakeup_copy = glo_ws_wakeup.copy()
    for ws in glo_ws_wakeup_copy:
        try:
            data = { "wakeup": wakeup }
            ws.send(json.dumps(data))
        except Exception:
            glo_ws_wakeup.remove(ws)


def _publish_is_wakeup_active_to_ws(is_wakeup_active: bool):
    glo_ws_wakeup_copy = glo_ws_wakeup.copy()
    for ws in glo_ws_wakeup_copy:
        try:
            data = { "is_wakeup_active": is_wakeup_active }
            ws.send(json.dumps(data))
        except Exception:
            glo_ws_wakeup.remove(ws)


def _set_alarm(is_alarm: bool, alarm_reason: str):
    """
    Set the alarm to True, publish through websocket, send value to InfluxDB.
    """

    state.set_alarm(is_alarm)
    state.set_alarm_reason(alarm_reason)
    _publish_alarm_to_ws(is_alarm, alarm_reason)

    # Write to influxDB.
    try:
        write_api = influx.write_api(write_options=SYNCHRONOUS)
        point = (
            Point("alarm").field("is_alarm", int(state.alarm)) # Influxdb REQUIRES AT LEAST 1 FIELD!
        )
        write_api.write(bucket=cfg['influxdb']['bucket'], org=cfg['influxdb']['org'], record=point)

    except Exception:
        print("Error")


def _set_wakeup(wakeup: str):
    state.set_wakeup(wakeup)
    _publish_wakeup_to_ws(wakeup)


def _set_is_wakeup_active(is_wakeup_active: bool):
    state.set_is_wakeup_active(is_wakeup_active)
    _publish_is_wakeup_active_to_ws(is_wakeup_active)


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
        alarm_reason = ''
        if is_alarm == True:
            alarm_reason = request.json.get('alarm_reason', 'unknown')
        # NOTE: 'unknown' is treated as the highest alarm reason. The only other reason we use so far is
        #       DS1/DS2 for unlocked doors, which are to be replaced by 'unknown' if they're currently in state.
        if state.alarm != is_alarm or (alarm_reason == 'unknown' and (state.alarm_reason == 'DS1' or state.alarm_reason == 'DS2')):
            _set_alarm(is_alarm, alarm_reason)
        return ""
    

@app.route("/wakeup", methods = ['GET', 'POST'])
def wakeup():
    if request.method == 'GET':
        return { "wakeup": state.wakeup }
    elif request.method == 'POST':
        wakeup = request.json['wakeup']
        if state.wakeup != wakeup:
            _set_wakeup(wakeup)
        return ""


@app.route("/is_wakeup_active", methods = ['GET', 'POST'])
def is_wakeup_active():
    if request.method == 'GET':
        return { "is_wakeup_active": state.is_wakeup_active }
    elif request.method == 'POST':
        is_wakeup_active = request.json['is_wakeup_active']
        if state.is_wakeup_active != is_wakeup_active:
            _set_is_wakeup_active(is_wakeup_active)
        return ""


@app.route("/rpir", methods = ['POST'])
def on_rpir_motion_detected():
    if request.method == 'POST':
        if state.number_of_people == 0 and not state.alarm:
            _set_alarm(True, 'unknown')
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
        _publish_alarm_to_ws(state.alarm, state.alarm_reason)
    
    while True:
        time.sleep(10)

    glo_ws_alarms.remove(ws)


@sock.route("/ws/wakeup")
def ws_wakeup(ws):
    global glo_ws_wakeup
    glo_ws_wakeup.append(ws)

    if state.wakeup:
        _publish_wakeup_to_ws(state.wakeup)
    if state.is_wakeup_active:
        _publish_is_wakeup_active_to_ws(state.is_wakeup_active)
    while True:
        time.sleep(10)


@sock.route("/ws/state")
def ws_state(ws):
    while True:
        d = {
            "alarm": state.alarm,
            "number_of_people": state.number_of_people,
            "device_state": state.device_state,
            "dms_last_4": state.dms_last_4.as_str(),
            "dms_cur_idx": state.dms_last_4.cur_idx
        }
        ws.send(json.dumps(d))
        time.sleep(1)


@sock.route("/ws/security")
def ws_security(ws):
    while True:
        d = {
            "security_active": state.security_active,
        }
        ws.send(json.dumps(d))
        time.sleep(10)


if __name__ == '__main__':
    t = threading.Thread(target=_periodically_set_state_pir_to_false, daemon=True)
    t.start()

    app.run(debug=True, use_reloader=False, host="127.0.0.1")