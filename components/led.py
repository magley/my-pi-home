from RPi import GPIO


def get_turn_on(cfg: dict):
    if cfg['simulated']:
        return turn_on_simulated
    return lambda: turn_on(cfg['pins'][0])


def get_turn_off(cfg: dict):
    if cfg['simulated']:
        return turn_off_simulated
    return lambda: turn_off(cfg['pins'][0])


def setup(pin: int):
    GPIO.setup(pin, GPIO.OUT)


def turn_on(pin: int):
    GPIO.output(pin, GPIO.HIGH)


def turn_off(pin: int):
    GPIO.output(pin, GPIO.LOW)


def turn_on_simulated():
    pass


def turn_off_simulated():
    pass