import typing
import actuators.buzzer as buzzer
import functools
import time
import config
import threading
from common import MyPiEvent, MyPiEventType


def setup(config: config.SensorConfig):
    if not config.simulated:
        buzzer.setup(config.pins[0])


def buzz(config: config.SensorConfig):
    buzzer.do_buzz_simulated() if config.simulated else buzzer.do_buzz(config.pins[0])


def stop_buzz(config: config.SensorConfig):
    buzzer.stop_buzz_simulated() if config.simulated else buzzer.stop_buzz(config.pins[0])
