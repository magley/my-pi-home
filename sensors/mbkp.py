import RPi.GPIO as GPIO
import typing
import random


KEYPAD_CHARS = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D'],
]


class OutputPins(typing.NamedTuple):
    r1: int
    r2: int
    r3: int
    r4: int


class InputPins(typing.NamedTuple):
    c1: int
    c2: int
    c3: int
    c4: int


class OutputRowPin(typing.NamedTuple):
    idx: int
    pin: int


def setup(output_pins: OutputPins, input_pins: InputPins):
    for pin in output_pins:
        GPIO.setup(pin, GPIO.OUT)
    for pin in input_pins:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def _read(row: OutputRowPin, input_pins: InputPins):
    GPIO.output(row.pin, GPIO.HIGH)
    res = [KEYPAD_CHARS[row.idx][idx] for idx, pin in enumerate(input_pins) if GPIO.input(pin) == 1]
    GPIO.output(row.pin, GPIO.LOW)
    return ''.join(res)


def read(output_pins: OutputPins, input_pins: InputPins):
    return ''.join([_read(OutputRowPin(idx, r), input_pins) for idx, r in enumerate(output_pins)])


def read_simulator():
    res = ''
    for _ in range(random.randint(1, 8)):
        row = random.randint(0, 3)
        key = random.randint(0, 3)
        res += KEYPAD_CHARS[row][key]
    return res
