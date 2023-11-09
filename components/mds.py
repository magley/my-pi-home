# MDS = Magnetic Door Sensor i.e. Door Sensor

import typing
import sensors.mds as mds
import functools
import time
import config
import threading
from common import MyPiEvent, MyPiEventType


def run(config: config.SensorConfig, event: MyPiEvent, lock: threading.Lock, on_read: typing.Callable):
    """
    `on_read` is a callback function invoked whenever door status data is read.
    It takes 1 argument denoting the state (open/close).
    """

    reader = _get_reader(config, on_read)
    while True:
        if event.is_set(MyPiEventType.STOP):
            print('Stopping mds loop')
            break
        reader()
        time.sleep(config.read_interval)


def _get_reader(config: config.SensorConfig, on_read: typing.Callable):
    if not config.simulated:
        return functools.partial(mds.read, pin=config.pin, on_read=on_read)
    else:
        return functools.partial(mds.read_simulator, pin=config.pin, on_read=on_read)