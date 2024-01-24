import RPi.GPIO as GPIO
import random
from common.mqtt import MqttSender, build_payload


class MDS_Mqtt(MqttSender):
    def __init__(self, config: dict):
        super().__init__(config)
        self.topic = "iot/mds"


    def put(self, cfg: dict, data: dict):
        if cfg['type'] != 'mds':
            return

        open_payload = build_payload(cfg, data, "open")
        self.do_put(open_payload)


def get_reader_func(cfg: dict):
    if cfg['simulated']:
        return read_sim
    return lambda: read_real(cfg['pins'][0])


def _reading(open: int):
    return { "open": open }


_is_pressed = [False]
def button_pressed(pin):
    global _is_pressed
    v = (GPIO.input(pin) == 0)
    _is_pressed.append(v)

    # if len(_is_pressed) > 10:
    #    _is_pressed = _is_pressed[]



def setup(pin: int):
    GPIO.setup(pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.add_event_detect(pin, GPIO.BOTH, callback=button_pressed, bouncetime=100)


def read_sim():
    return _reading(random.randint(0, 1))


def read_real(pin: int):
    print(_is_pressed[-1])
    return _reading(1 if _is_pressed[-1] else 0)

"""
GPIO.add_event_detect(BUTTON_PIN, GPIO.BOTH, callback=button_pressed, bouncetime=100)
def button_pressed(pin):
    released = GPIO.input(BUTTON_PIN))
"""