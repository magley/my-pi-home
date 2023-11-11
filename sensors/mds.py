import RPi.GPIO as GPIO
import random


def read(pin: int):
    # Works as a button, but we care about its current state, not the event.

    GPIO.setup(pin, GPIO.IN)
    return GPIO.input(pin)


def read_simulator():
    return random.randint(0, 1)