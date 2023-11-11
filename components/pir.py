import typing
import sensors.pir as pir
import functools
import time
import config
import threading
from common import MyPiEvent, MyPiEventType

def setup(config: config.SensorConfig, when_motion: typing.Callable):
    if not config.simulated:
        pir.setup(config.pins[0], when_motion)
    else:
        pir.setup_simulator(when_motion)
