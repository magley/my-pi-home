from RPi import GPIO


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
