import json
import dataclasses


@dataclasses.dataclass
class SensorConfig:
    name: str
    pin: int
    simulated: bool
    read_interval: int


def load_configs(path):
    return [SensorConfig(**x) for x in json.load(open(path))]
