import time
import typing
from RPi import GPIO


def buzz(pin: int):
    GPIO.setup(pin, GPIO.OUT)

    def do_buzz():
        GPIO.output(pin, GPIO.HIGH)

    def stop_buzz():
        GPIO.output(pin, GPIO.HIGH)

    return (do_buzz, stop_buzz)


def buzz_simulator(pin: int):
    def do_buzz():
        print(f"{time.strftime('%H:%M:%S', time.localtime())} Start buzzing on pin {pin}")

    def stop_buzz():
        print(f"{time.strftime('%H:%M:%S', time.localtime())} Stop buzzing on pin {pin}")
    
    return (do_buzz, stop_buzz)