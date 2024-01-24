import random
import RPi.GPIO as GPIO
import time
from common.mqtt import MqttSender, build_payload


class DHT_Mqtt(MqttSender):
    def __init__(self, config: dict):
        super().__init__(config)
        self.topic = "iot/dht"


    def put(self, cfg: dict, data: dict):
        if cfg['type'] != 'dht':
            return

        temperature_payload = build_payload(cfg, data, "temperature")
        self.do_put(temperature_payload)

        humidity_payload = build_payload(cfg, data, "humidity")
        self.do_put(humidity_payload)


def get_reader_func(cfg: dict):
    if cfg['simulated']:
        return read_sim
    return lambda: read_real(cfg['pins'][0])


def _reading(temp: int, humidity: int):
    return { "temperature": temp, "humidity": humidity }


def setup(pin: int):
    pass


def read_sim():
    return _reading(random.uniform(25, 30), random.uniform(30, 50))


def read_real(pin: int):
    wakeup_delay = 0.020
    timeout = 0.0001
    mask = 0x80
    idx = 0
    bits = [0, 0, 0, 0, 0]

    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
    time.sleep(wakeup_delay)
    GPIO.output(pin, GPIO.HIGH)
    GPIO.setup(pin, GPIO.IN)

    t = time.time()
    while GPIO.input(pin) == GPIO.LOW:
        if (time.time() - t) > timeout:
            return _reading(0, 0)
    t = time.time()
    while GPIO.input(pin) == GPIO.HIGH:
        if (time.time() - t) > timeout:
            return _reading(0, 0)
    for i in range(0, 40, 1):
        t = time.time()
        while GPIO.input(pin) == GPIO.LOW:
            if (time.time() - t) > timeout:
                return _reading(0, 0)
        t = time.time()
        while GPIO.input(pin) == GPIO.HIGH:
            if (time.time() - t) > timeout:
                return _reading(0, 0)
        if (time.time() - t) > 0.00005:
            bits[idx] |= mask
        mask >>= 1
        if mask == 0:
            mask = 0x80
            idx += 1
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)
    sum_chk = (bits[0] + bits[1] + bits[2] + bits[3]) & 0xFF
    if bits[4] is not sum_chk:
        return _reading(0, 0)
    humidity = bits[0]
    temperature = bits[2] + bits[3] * 0.1
    return _reading(humidity, temperature)
