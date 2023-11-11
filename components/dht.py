import sensors.dht as dht
import functools
import time
import typing
import config
from common import MyPiEvent, MyPiEventType


def run(config: config.SensorConfig, event: MyPiEvent, on_read: typing.Callable[[dht.DHTReading], None]):
    reader = _get_reader(config)

    while True:
        if event.is_set(MyPiEventType.STOP):
            print('Stopping dht loop')
            break
        reading = reader()
        on_read(reading)
        time.sleep(config.read_interval)


ReaderCallback = typing.Callable[[], dht.DHTReading]


# TODO: Possible type shadowing?
def _get_reader(config: config.SensorConfig) -> ReaderCallback:
    if not config.simulated:
        return functools.partial(dht.read_dht, pin=config.pins[0])
    else:
        return dht.Simulator().read_dht
