import sensors.dht as dht
import functools
import time
import asyncio
import typing
import config


async def start_runner(config: config.SensorConfig):
    reader = _get_appropriate_reader(config)
    await _runner(reader)


def print_reading(reading: dht.DHTReading):
    t = time.localtime()
    print("="*20)
    print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
    print(f"Code: {reading.code}")
    print(f"Humidity: {reading.humidity}%")
    print(f"Temperature: {reading.temperature}°C")


ReaderCallback = typing.Callable[[], dht.DHTReading]


async def _runner(reader: ReaderCallback):
    while True:
        reading = reader()
        print_reading(reading)
        await asyncio.sleep(2)


def _make_reader(pin: int):
    return functools.partial(dht.read_dht, pin=pin)


# NOTE: Am I doing type shadowing here? The returns of both read_dht_simulated and
#       _make_reader should be compatible with ReaderCallback, yet if I make
#       read_dht_simulated return a different type than expected the MyPy static
#       type checker doesn't complain.
def _get_appropriate_reader(config: config.SensorConfig) -> ReaderCallback:
    return _make_reader(config.pin) if not config.simulated else dht.read_dht_simulated
