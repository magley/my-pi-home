import dataclasses
import json


@dataclasses.dataclass
class DeviceConfig:
    name: str
    type: str
    pins: list[int]
    simulated: bool
    read_interval: float
    runs_on: str


@dataclasses.dataclass
class MqttConfig:
    host: str
    port: str
    topics: dict[str, str]


@dataclasses.dataclass
class Config:
    mqtt: MqttConfig
    devices: dict[str, DeviceConfig]

    def __init__(self):
        pass


def load_configs(path):
    d = json.load(open(path))
    res = Config()
    
    res.mqtt = MqttConfig(**d['mqtt'])
    res.devices = {
        x['name']: DeviceConfig(**x) for x in d['devices']
    }

    return res
