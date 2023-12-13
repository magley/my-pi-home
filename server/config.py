import json


def load_config(path, influx_token_secret_path):
    cfg = json.load(open(path))

    with open(influx_token_secret_path, "r") as f:
        cfg['influxdb']['token'] = f.read()

    return cfg