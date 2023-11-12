# MDS = Magnetic Door Sensor i.e. Door Sensor

import typing
import sensors.mds as mds
import functools
import time
from util.common import SensorConfig


def run(config: SensorConfig, on_read: typing.Callable[[SensorConfig, int], None]):
    """
    `on_read` is a callback function invoked whenever door status data is read.
    It takes 1 argument denoting the state (open/close).
    """

    reader = _get_reader(config)
    while True:
        reading = reader()
        on_read(config, reading)
        time.sleep(config.read_interval)


def _get_reader(config: SensorConfig):
    if not config.simulated:
        return functools.partial(mds.read, pin=config.pins[0])
    else:
        return mds.read_simulator