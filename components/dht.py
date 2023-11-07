import sensors.dht as dht
import functools
import time
import typing
import config
import threading


def run(config: config.SensorConfig, stop_event: threading.Event, lock: threading.Lock):
    reader = _get_reader(config)

    while True:
        if stop_event.is_set():
            print('Stopping dht loop')
            break
        reading = reader()
        _print_reading(reading, config, lock)
        time.sleep(config.read_interval)


def _print_reading(reading: dht.DHTReading, config: config.SensorConfig, lock: threading.Lock):
    t = time.localtime()

    with lock:
        print("-" * 25)
        print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
        print(f"Sensor: {config.name}")
        print(f"Code: {reading.code}")
        print(f"Humidity: {reading.humidity}%")
        print(f"Temperature: {reading.temperature}°C")


ReaderCallback = typing.Callable[[], dht.DHTReading]


# TODO: Possible type shadowing?
def _get_reader(config: config.SensorConfig) -> ReaderCallback:
    if not config.simulated:
        return functools.partial(dht.read_dht, pin=config.pin)
    else:
        return dht.Simulator().read_dht
