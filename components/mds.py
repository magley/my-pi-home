import RPi.GPIO as GPIO
import random


def get_reader_func(cfg: dict):
    if cfg['simulated']:
        return read_sim
    return lambda: read_real(cfg['pins'][0])


def _reading(open: int):
    return { "open": open }


def setup(pin: int):
    GPIO.setup(pin, GPIO.IN)


def read_sim():
    return _reading(random.randint(0, 1))


def read_real(pin: int):
    # Works as a button, but we care about its current state and not the event.
    return _reading(GPIO.input(pin))