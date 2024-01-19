# NOTE: This is a stub for the RPi.GPIO module. It should *not* be copied to the RasPi

OUT = 0
LOW = 1
HIGH = 2
IN = 3
BCM = 4
RISING = 5
FALLING = 6
PUD_DOWN = 7
PUD_UP = 8
BOTH = 9

def setmode(mode):
    pass


def setup(pin, kind, pull_up_down=None):
    pass


def output(pin, val):
    pass


def input(pin) -> int:
    return 0


def add_event_detect(pin, condition, callback, bouncetime=100):
    pass


def cleanup():
    pass


def setwarnings(should_warn: bool):
    pass