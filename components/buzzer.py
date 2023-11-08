import typing
import actuators.buzzer as buzzer
import functools
import time
import config
import threading
from common import MyPiEvent, MyPiEventType


def run(config: config.SensorConfig, event: MyPiEvent, lock: threading.Lock):
    """
    `when_motion` is a callback function invoked whenever motion is detected. It takes no arguments.
    """

    on_buzz, on_stop_buzz = _get_buzzer(config)
    while True:
        if event.is_set(MyPiEventType.STOP):
            print('Stopping buzzer loop')
            break
    
        if event.is_set(MyPiEventType.BUZZ) and event.pin == config.pin:
            on_buzz()
            event.consume()
        elif event.is_set(MyPiEventType.STOP_BUZZ) and event.pin == config.pin:
            on_stop_buzz()
            event.consume()

        time.sleep(config.read_interval)


def _get_buzzer(config: config.SensorConfig) -> typing.Tuple[typing.Callable, typing.Callable]:
    """
    Returns a tuple of 2 functions: on_buzz, on_stop_buzz.
    Each should get called when the buzz/stop buzz event is set.
    """

    if not config.simulated:
        return buzzer.buzz(config.pin)
    else:
        return buzzer.buzz_simulator(config.pin)