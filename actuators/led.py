import threading
import time
from RPi import GPIO
import threading


def setup(pin: int):
    GPIO.setup(pin, GPIO.OUT)


def turn_on(pin: int):
    GPIO.output(pin, GPIO.HIGH)


def turn_off(pin: int):
    GPIO.output(pin, GPIO.LOW)


def turn_on_simulated():
    pass


def turn_off_simulated():
    pass
