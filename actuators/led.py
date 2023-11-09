import threading
import time
from RPi import GPIO


def light(pin: int):
    GPIO.setup(pin, GPIO.OUT)

    def turn_on():
        GPIO.output(pin, GPIO.HIGH)

    def turn_off():
        GPIO.output(pin, GPIO.LOW)

    return (turn_on, turn_off)


def light_simulator(pin: int, print_lock: threading.Lock):
    def turn_on():
        with print_lock:
            print(f"{time.strftime('%H:%M:%S', time.localtime())} Turn on LED on pin {pin}")

    def turn_off():
        with print_lock:
            print(f"{time.strftime('%H:%M:%S', time.localtime())} Turn off LED on pin {pin}")
    
    return (turn_on, turn_off)