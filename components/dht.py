import sensors.dht as dht
import functools
import time
import typing
import config
import threading
from common import MyPiEvent, MyPiEventType


def run(config: config.SensorConfig, event: MyPiEvent, lock: threading.Lock):
    reader = _get_reader(config)

    while True:
        if event.is_set(MyPiEventType.STOP):
            print('Stopping dht loop')
            break
        reading = reader()
        _print_reading(reading, config, lock)
        time.sleep(config.read_interval)


def _print_reading(reading: dht.DHTReading, config: config.SensorConfig, lock: threading.Lock):
    t = time.localtime()

    with lock:
        print(f"{time.strftime('%H:%M:%S', t)} {config.name} {reading.humidity}% {reading.temperature}°C")


ReaderCallback = typing.Callable[[], dht.DHTReading]


# TODO: Possible type shadowing?
def _get_reader(config: config.SensorConfig) -> ReaderCallback:
    if not config.simulated:
        return functools.partial(dht.read_dht, pin=config.pin)
    else:
        return dht.Simulator().read_dht
