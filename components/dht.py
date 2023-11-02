import sensors.dht as dht
import functools
import time
import typing
import config
import threading


def start_reader_loop(config: config.SensorConfig, stop_event: threading.Event):
    reader = _get_appropriate_reader(config)
    _reader_loop(reader, config, stop_event)


def print_reading(reading: dht.DHTReading, config: config.SensorConfig):
    t = time.localtime()
    print("="*20)
    print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
    print(f"Sensor: {config.name}")
    print(f"Code: {reading.code}")
    print(f"Humidity: {reading.humidity}%")
    print(f"Temperature: {reading.temperature}°C")


ReaderCallback = typing.Callable[[], dht.DHTReading]


def _reader_loop(reader: ReaderCallback, config: config.SensorConfig, stop_event: threading.Event):
    while True:
        if stop_event.is_set():
            print('Stopping dht loop')
            break
        reading = reader()
        print_reading(reading, config)
        time.sleep(config.read_interval)


# NOTE: Am I doing type shadowing here? The returns of both read_dht_simulated and
#       _make_reader should be compatible with ReaderCallback, yet if I make
#       read_dht_simulated return a different type than expected the MyPy static
#       type checker doesn't complain.
def _get_appropriate_reader(config: config.SensorConfig) -> ReaderCallback:
    if not config.simulated:
        return functools.partial(dht.read_dht, pin=config.pin)
    else:
        return dht.Simulator().read_dht
