import threading
import time
from RPi import GPIO


def buzz(pin: int):
    GPIO.setup(pin, GPIO.OUT)

    def do_buzz():
        GPIO.output(pin, GPIO.HIGH)

    def stop_buzz():
        GPIO.output(pin, GPIO.HIGH)

    return (do_buzz, stop_buzz)


def buzz_simulator(pin: int, print_lock: threading.Lock):
    def do_buzz():
        with print_lock:
            print(f"{time.strftime('%H:%M:%S', time.localtime())} Start buzzing on pin {pin}")

    def stop_buzz():
        with print_lock:
            print(f"{time.strftime('%H:%M:%S', time.localtime())} Stop buzzing on pin {pin}")
    
    return (do_buzz, stop_buzz)