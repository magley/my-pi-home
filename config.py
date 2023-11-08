import json
import dataclasses


@dataclasses.dataclass
class SensorConfig:
    name: str
    type: str
    pin: int
    simulated: bool
    read_interval: float


def load_configs(path):
    list_of_dict = json.load(open(path))
    res = {
        x['name']: SensorConfig(**x) for x in list_of_dict
    }

    return res