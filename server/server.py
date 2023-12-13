from flask import Flask
import json
import config
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import paho.mqtt.client as mqtt


app = Flask(__name__)
cfg = config.load_config("config.json", "influx_token.secret")

data = []

# Influx
influx = InfluxDBClient(url=cfg['influxdb']['url'], token=cfg['influxdb']['token'], org=cfg['influxdb']['org'])

# MQTT
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("iot/dht")

def on_message(client, userdata, msg):
    data.append(msg.topic + " " + str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(cfg['mqtt']['host'], cfg['mqtt']['port'], 60)
client.loop_start()


@app.route('/')
def hello():
    return json.dumps(data)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)