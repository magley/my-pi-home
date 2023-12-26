from flask import Flask, request
import json
import config
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import paho.mqtt.client as mqtt
from state import State


app = Flask(__name__)
cfg = config.load_config("config.json", "influx_token.secret")


###############################################################################
# InfluxDB
###############################################################################

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

###############################################################################
# MQTT
###############################################################################

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

###############################################################################
# API
###############################################################################

state = State()


@app.route("/people", methods = ['GET', 'POST'])
def get_number_of_people():
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
    


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)