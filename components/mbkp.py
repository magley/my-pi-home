import random
import RPi.GPIO as GPIO


def get_reader_func(cfg: dict):
    if cfg['simulated']:
        return read_sim
    return lambda: read_real(cfg['pins'][:4], cfg['pins'][4:])


def _reading(keys: str):
    return { "keys": keys }


KEYPAD_CHARS = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D'],
]


def setup(output_pins, input_pins):
    for pin in output_pins:
        GPIO.setup(pin, GPIO.OUT)
    for pin in input_pins:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def read_sim():
    res = ''
    for _ in range(random.randint(1, 8)):
        row = random.randint(0, 3)
        key = random.randint(0, 3)
        res += KEYPAD_CHARS[row][key]
    return _reading(res)


def read_real(output_pins, input_pins):
    def _read_row(row: int, row_output_pin: int, input_pins: list[int]):
        GPIO.output(row_output_pin, GPIO.HIGH)
        res = []
        for idx, pin in enumerate(input_pins):
            if GPIO.input(pin) == 1:
                res.append(KEYPAD_CHARS[row][idx])
        GPIO.output(row_output_pin, GPIO.LOW)
        return ''.join(res)
    
    res = ''
    for idx, r in enumerate(output_pins):
        res += _read_row(idx, r, input_pins)
    return _reading(res)