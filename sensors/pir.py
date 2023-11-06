import RPi.GPIO as GPIO
import typing
import time
import enum
import random


class PIRReading(typing.NamedTuple):
    motion: bool


def read(pin: int, when_motion = None, when_no_motion = None) -> PIRReading:
    GPIO.setup(pin, GPIO.IN)

    if when_motion is not None:
        GPIO.add_event_detect(pin, GPIO.RISING, callback=when_motion)
    if when_no_motion is not None:
        GPIO.add_event_detect(pin, GPIO.FALLING, callback=when_no_motion)

    time.sleep(0.5)

    if GPIO.input(pin) == GPIO.HIGH:
        return PIRReading(True)
    else:
        return PIRReading(False)


class Simulator:
    def __init__(self, when_motion = None, when_no_motion = None):
        self.motion = False
        self.when_motion = when_motion
        self.when_no_motion = when_no_motion


    def read(self) -> PIRReading:
        if random.randint(0, 5) == 0:
            if  self.motion:
                if self.when_motion is not None:
                    self.when_motion()
                self.motion = True
            else:
                self.motion = False
                if self.when_no_motion is not None:
                    self.when_no_motion()

        return PIRReading(self.motion)