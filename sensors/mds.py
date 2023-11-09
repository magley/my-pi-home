import typing
import RPi.GPIO as GPIO
import random


def read(pin: int, on_read: typing.Callable):
    # Works as a button, but we care about its current state, not the event.

    GPIO.setup(pin, GPIO.IN)
    on_read(GPIO.input(pin))


def read_simulator(pin: int, on_read: typing.Callable):
    on_read(random.randint(0, 1))