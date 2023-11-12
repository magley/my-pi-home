import RPi.GPIO as GPIO
import random


def setup(pin: int):
    GPIO.setup(pin, GPIO.IN)


def read(pin: int):
    # Works as a button, but we care about its current state, not the event.
    return GPIO.input(pin)


def read_simulator():
    return random.randint(0, 1)
