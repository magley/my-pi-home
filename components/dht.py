import random
import RPi.GPIO as GPIO
import time


def get_reader_func(cfg: dict):
    if cfg['simulated']:
        return read_sim
    return lambda: read_real(cfg['pins'][0])


def _reading(temp: int, humidity: int):
    return { "temperature": temp, "humidity": humidity }


def setup(pin: int):
    pass


def read_sim():
    return _reading(random.randint(25, 30), random.randint(30, 50))


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
