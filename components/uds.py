from common import SensorConfig
import typing
import sensors.uds as uds
import functools
import time


def run(config: SensorConfig, on_read: typing.Callable[[SensorConfig, uds.UDSReading], None]):
    reader = _get_reader(config)
    while True:
        reading = reader()
        on_read(config, reading)
        time.sleep(config.read_interval)


def _get_reader(config: SensorConfig):
    if not config.simulated:
        return functools.partial(uds.read, pin_trig=config.pins[0], pin_echo=config.pins[1])
    else:
        return uds.read_simulator
