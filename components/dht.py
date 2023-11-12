import sensors.dht as dht
import functools
import time
import typing
from common import SensorConfig


def run(config: SensorConfig, on_read: typing.Callable[[SensorConfig, dht.DHTReading], None]):
    reader = _get_reader(config)
    while True:
        reading = reader()
        on_read(config, reading)
        time.sleep(config.read_interval)


ReaderCallback = typing.Callable[[], dht.DHTReading]


# TODO: Possible type shadowing?
def _get_reader(config: SensorConfig) -> ReaderCallback:
    if not config.simulated:
        return functools.partial(dht.read_dht, pin=config.pins[0])
    else:
        return dht.Simulator().read_dht
