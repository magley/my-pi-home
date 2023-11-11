import typing
import RPi.GPIO as GPIO
import random
import threading
import time


def setup(pin: int, when_motion: typing.Callable):
    GPIO.setup(pin, GPIO.IN)
    GPIO.add_event_detect(pin, GPIO.RISING, callback=when_motion)


def setup_simulator(when_motion: typing.Callable):
    def read():
        while True:
            if random.randint(1, 3) == 1:
                when_motion()
            time.sleep(1)
    threading.Thread(target=read, daemon=True).start()
