import RPi.GPIO as GPIO
import time
import typing
import enum
import random


WAKEUP = 0.2
MISC = 0.00001  # FIXME: What is this delay for?


class UDSCode(enum.Enum):
    OK = enum.auto()
    TIMED_OUT = enum.auto()


class UDSReading(typing.NamedTuple):
    code: UDSCode
    distance: float


def read(pin_trig: int, pin_echo: int, wakeup_delay = WAKEUP, misc_delay = MISC):
    GPIO.setup(pin_trig, GPIO.OUT)
    GPIO.setup(pin_echo, GPIO.IN)

    GPIO.output(pin_trig, False)
    time.sleep(wakeup_delay)
    GPIO.output(pin_trig, True)
    time.sleep(misc_delay)
    GPIO.output(pin_trig, False)
    pulse_start_time = time.time()
    pulse_end_time = time.time()

    max_iter = 100

    iter = 0
    while GPIO.input(pin_echo) == 0:
        if iter > max_iter:
            return UDSReading(UDSCode.TIMED_OUT, 0)
        pulse_start_time = time.time()
        iter += 1

    iter = 0
    while GPIO.input(pin_echo) == 1:
        if iter > max_iter:
            return UDSReading(UDSCode.TIMED_OUT, 0)
        pulse_end_time = time.time()
        iter += 1

    pulse_duration = pulse_end_time - pulse_start_time
    distance = (pulse_duration * 34300)/2
    return UDSReading(UDSCode.OK, distance)


def read_simulator():
    return UDSReading(UDSCode.OK, random.randint(10000, 20000))
