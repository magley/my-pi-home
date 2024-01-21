import RPi.GPIO as GPIO
from common.mqtt import MqttSender, build_payload
import time


class D4S7_Mqtt(MqttSender):
    def __init__(self, config: dict):
        super().__init__(config)
        self.topic = "iot/d4s7"


    # Actuactor can have multiple events, so pass the event as well
    def put(self, cfg: dict, data: dict, event: str):
        if cfg['type'] != 'd4s7':
            return

        payload = build_payload(cfg, data, event)
        self.do_put(payload)


def setup(segment_pins: list[int], digit_pins: list[int], is_simulated: bool):
    if is_simulated:
        return
    for pin in segment_pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)
    for pin in digit_pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 1)

NUM = {
    ' ':(0,0,0,0,0,0,0),
    '0':(1,1,1,1,1,1,0),
    '1':(0,1,1,0,0,0,0),
    '2':(1,1,0,1,1,0,1),
    '3':(1,1,1,1,0,0,1),
    '4':(0,1,1,0,0,1,1),
    '5':(1,0,1,1,0,1,1),
    '6':(1,0,1,1,1,1,1),
    '7':(1,1,1,0,0,0,0),
    '8':(1,1,1,1,1,1,1),
    '9':(1,1,1,1,0,1,1)
    }


def get_set_digits(cfg: dict):
    if cfg['simulated']:
        return set_digits_simulated
    return set_digits


# Copied (as much as possible) from course materials.
def set_digits(text: str, segments: list[int], digits: list[int], dot_pin: int):
    """
    text is in format HH:MM:SS (ex. 09:54:13)
    """
    s = text[0:2] + text[3:5]
    last_second = int(text[-1:])
    for digit in range(4):
        for loop in range(0,7):
            GPIO.output(segments[loop], NUM[s[digit]][loop])
            if (last_second % 2 == 0) and (digit == 1):
                GPIO.output(dot_pin, 1)
            else:
                GPIO.output(dot_pin, 0)
        GPIO.output(digits[digit], 0)
        time.sleep(0.001)
        GPIO.output(digits[digit], 1)


def set_digits_simulated(text: str, segments: list[int], digits: list[int], dot_pin: int):
    pass


def get_blank_display(cfg: dict):
    if cfg['simulated']:
        return set_blank_display_simulated
    return set_blank_display


def set_blank_display(segments: list[int], digits: list[int]):
    for digit in range(4):
        for loop in range(0, 7):
            GPIO.output(segments[loop], 0)
        GPIO.output(digits[digit], 0)
        time.sleep(0.001)
        GPIO.output(digits[digit], 1)


def set_blank_display_simulated(segments: list[int], digits: list[int]):
    pass
