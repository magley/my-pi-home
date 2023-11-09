import typing
import actuators.led as led
import functools
import time
import config
import threading
from common import MyPiEvent, MyPiEventType


def run(config: config.SensorConfig, event: MyPiEvent, print_lock: threading.Lock):
    turn_on, turn_off = _get_led(config, print_lock)
    while True:
        if event.is_set(MyPiEventType.STOP):
            print('Stopping led loop')
            break
    
        if event.is_set(MyPiEventType.LED_ON) and event.pin == config.pin:
            turn_on()
            event.consume()
        elif event.is_set(MyPiEventType.LED_OFF) and event.pin == config.pin:
            turn_off()
            event.consume()

        time.sleep(config.read_interval)


def _get_led(config: config.SensorConfig, print_lock: threading.Lock) -> typing.Tuple[typing.Callable, typing.Callable]:
    """
    Returns a tuple of 2 functions: turn_on, turn_off.
    Each should get called when the LED turn on/off event is set.
    """

    if not config.simulated:
        return led.light(config.pin)
    else:
        return led.light_simulator(config.pin, print_lock)