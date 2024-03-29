import random
import RPi.GPIO as GPIO
import time
from common.mqtt import MqttSender, build_payload


class UDS_Mqtt(MqttSender):
    def __init__(self, config: dict):
        super().__init__(config)
        self.topic = "iot/uds"


    def put(self, cfg: dict, data: dict):
        if cfg['type'] != 'uds':
            return

        distance_payload = build_payload(cfg, data, "distance_in_cm")
        self.do_put(distance_payload)

        code_payload = build_payload(cfg, data, "code")
        self.do_put(code_payload)


def get_reader_func(cfg: dict):
    if cfg['simulated']:
        return read_sim
    return lambda: read_real(cfg['pins'][0], cfg['pins'][1])


def _reading(distance_in_cm: float, code: int):
    return { "distance_in_cm": distance_in_cm, "code": code }


def setup(pin_trig: int, pin_echo: int):
    GPIO.setup(pin_trig, GPIO.OUT)
    GPIO.setup(pin_echo, GPIO.IN)


def read_sim():
    return _reading(20 + random.random() * 10, 0)


WAKEUP_DELAY = 0.2
SOUNDWAVE_DELAY = 0.00001
SPEED_OF_SOUND_MAYBE = 34300


def read_real(pin_trig: int, pin_echo: int):
    GPIO.output(pin_trig, False)
    time.sleep(WAKEUP_DELAY)
    GPIO.output(pin_trig, True)
    time.sleep(SOUNDWAVE_DELAY)
    GPIO.output(pin_trig, False)
    pulse_start_time = time.time()
    pulse_end_time = time.time()

    max_iter = 100

    iter = 0
    while GPIO.input(pin_echo) == 0:
        if iter > max_iter:
            return _reading(0, -1)
        pulse_start_time = time.time()
        iter += 1

    iter = 0
    while GPIO.input(pin_echo) == 1:
        if iter > max_iter:
            return _reading(0, -1)
        pulse_end_time = time.time()
        iter += 1

    pulse_duration = pulse_end_time - pulse_start_time
    distance = (pulse_duration * SPEED_OF_SOUND_MAYBE)/2
    return _reading(distance, 0)