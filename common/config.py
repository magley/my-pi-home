import json


def load_configs(path):
    return json.load(open(path))