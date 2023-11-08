import typing
import RPi.GPIO as GPIO
import random


def read(pin: int, when_motion: typing.Callable):
    GPIO.setup(pin, GPIO.IN)
    GPIO.add_event_detect(pin, GPIO.RISING, callback=when_motion)


def read_simulator(pin: int, when_motion: typing.Callable):
    if random.randint(1, 3) == 1:
        when_motion()