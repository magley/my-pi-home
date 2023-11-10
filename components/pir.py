import typing
import sensors.pir as pir
import functools
import time
import config
import threading
from common import MyPiEvent, MyPiEventType


def run(config: config.SensorConfig, event: MyPiEvent, lock: threading.Lock, when_motion: typing.Callable):
    """
    `when_motion` is a callback function invoked whenever motion is detected. It takes no arguments.
    """

    reader = _get_reader(config, when_motion)
    while True:
        if event.is_set(MyPiEventType.STOP):
            print('Stopping pir loop')
            break
        reader()
        time.sleep(config.read_interval)


def _get_reader(config: config.SensorConfig, when_motion: typing.Callable):
    if not config.simulated:
        return functools.partial(pir.read, pin=config.pin, when_motion=when_motion)
    else:
        return functools.partial(pir.read_simulator, pin=config.pin, when_motion=when_motion)