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


def _read(row: OutputRowPin, input_pins: InputPins):
    c1, c2, c3, c4 = input_pins

    GPIO.output(row.pin, GPIO.HIGH)
    res: list[str] = []  # Assuming we can hold down multiple keys in one read
    if(GPIO.input(c1) == 1):
        res.append(KEYPAD_CHARS[row.idx][0])
    if(GPIO.input(c2) == 1):
        res.append(KEYPAD_CHARS[row.idx][1])
    if(GPIO.input(c3) == 1):
        res.append(KEYPAD_CHARS[row.idx][2])
    if(GPIO.input(c4) == 1):
        res.append(KEYPAD_CHARS[row.idx][3])
    GPIO.output(row.pin, GPIO.LOW)
    return res


def read(output_pins: OutputPins, input_pins: InputPins):
    r1, r2, r3, r4 = output_pins
    c1, c2, c3, c4 = input_pins

    # FIXME(?): Is calling setup on every call of read() going to break something?
    GPIO.setup(r1, GPIO.OUT)
    GPIO.setup(r2, GPIO.OUT)
    GPIO.setup(r3, GPIO.OUT)
    GPIO.setup(r4, GPIO.OUT)
    GPIO.setup(c1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(c2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(c3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(c4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    res: list[str] = []  # Assuming we can hold down multiple rows in one read
    res.extend(_read(OutputRowPin(0, r1), input_pins))
    res.extend(_read(OutputRowPin(1, r2), input_pins))
    res.extend(_read(OutputRowPin(2, r3), input_pins))
    res.extend(_read(OutputRowPin(3, r4), input_pins))
    return ''.join(res)


# Reads only one character per read, unlike unsimulated read
def read_simulator():
    row = random.randint(0, 3)
    key = random.randint(0, 3)
    return KEYPAD_CHARS[row][key]
