import RPi.GPIO as GPIO
import time
import typing
import enum
import random


WAKEUP_DELAY = 0.2
SOUNDWAVE_DELAY = 0.00001
SPEED_OF_SOUND_MAYBE = 34300


class UDSCode(enum.Enum):
    OK = enum.auto()
    TIMED_OUT = enum.auto()


class UDSReading(typing.NamedTuple):
    code: UDSCode
    distance_in_cm: float


def setup(pin_trig: int, pin_echo: int):
    GPIO.setup(pin_trig, GPIO.OUT)
    GPIO.setup(pin_echo, GPIO.IN)


def read(pin_trig: int, pin_echo: int, wakeup_delay = WAKEUP_DELAY, soundwave_delay = SOUNDWAVE_DELAY):
    GPIO.output(pin_trig, False)
    time.sleep(wakeup_delay)
    GPIO.output(pin_trig, True)
    time.sleep(soundwave_delay)
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
    distance = (pulse_duration * SPEED_OF_SOUND_MAYBE)/2
    return UDSReading(UDSCode.OK, distance)


def read_simulator():
    return UDSReading(UDSCode.OK, random.randint(2, 400))
