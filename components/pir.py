import typing
import RPi.GPIO as GPIO
import random
import threading
import time


'''
PIR doesn't have a loop, it uses callbacks to respond to motion.

When simulated, it starts a daemon thread firing a motion callback.
When real device, it adds an event callback.
'''


def setup(pin: int, simulated: bool, on_motion_callback: typing.Callable):
    if simulated:
        def sim_loop():
            while True:
                if random.randint(1, 3) == 1:
                    on_motion_callback()
                time.sleep(2)

        threading.Thread(target=sim_loop, daemon=True).start()
    else:
        GPIO.setup(pin, GPIO.IN)
        GPIO.add_event_detect(pin, GPIO.RISING, callback=on_motion_callback)

