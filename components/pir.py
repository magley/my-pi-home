import typing
import RPi.GPIO as GPIO
import random
import threading
import time


from common.mqtt import MqttSender, build_payload


class PIR_Mqtt(MqttSender):
    def __init__(self, config: dict):
        super().__init__(config)
        self.topic = "iot/pir"


    def put(self, cfg: dict, data: dict):
        if cfg['type'] != 'pir':
            return
        
        payload = build_payload(cfg, data, "motion")
        self.do_put(payload)


'''
PIR doesn't have a loop, it uses callbacks to respond to motion.

When simulated, it starts a daemon thread firing a motion callback.
When real device, it adds an event callback.
'''


def _reading():
    return { "motion": True }


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

