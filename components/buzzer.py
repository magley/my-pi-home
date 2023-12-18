from RPi import GPIO


def get_do_buzz(cfg: dict):
    if cfg['simulated']:
        return do_buzz_simulated
    return lambda: do_buzz(cfg['pins'][0])


def get_stop_buzz(cfg: dict):
    if cfg['simulated']:
        return stop_buzz_simulated
    return lambda: stop_buzz(cfg['pins'][0])


def setup(pin: int):
    GPIO.setup(pin, GPIO.OUT)


def do_buzz(pin: int):
    GPIO.output(pin, GPIO.HIGH)


def stop_buzz(pin: int):
    GPIO.output(pin, GPIO.LOW)


def do_buzz_simulated():
    pass


def stop_buzz_simulated():
    pass