from config import SensorConfig
from common import MyPiEvent, MyPiEventType
import typing
import sensors.uds as uds
import functools
import time


def run(config: SensorConfig, on_read: typing.Callable[[uds.UDSReading], None]):
    reader = _get_reader(config)
    while True:
        reading = reader()
        on_read(reading)
        time.sleep(config.read_interval)


def _get_reader(config: SensorConfig):
    if not config.simulated:
        return functools.partial(uds.read, pin_trig=config.pins[0], pin_echo=config.pins[1])
    else:
        return uds.read_simulator
