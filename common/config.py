import dataclasses
import json


@dataclasses.dataclass
class SensorConfig:
    name: str
    type: str
    pins: list[int]
    simulated: bool
    read_interval: float


def load_configs(path):
    list_of_dict = json.load(open(path))
    res = {
        x['name']: SensorConfig(**x) for x in list_of_dict
    }

    return res
