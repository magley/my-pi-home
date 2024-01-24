from RPi import GPIO
from common.mqtt import MqttSender, build_payload


class Buzzer_Mqtt(MqttSender):
    def __init__(self, config: dict):
        super().__init__(config)
        self.topic = "iot/buzzer"


    # Actuactor can have multiple events, so pass the event as well
    def put(self, cfg: dict, data: dict, event: str):
        if cfg['type'] != 'buzzer':
            return

        buzz_payload = build_payload(cfg, data, event)
        self.do_put(buzz_payload)


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
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)


def stop_buzz(pin: int):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)


def do_buzz_simulated():
    pass


def stop_buzz_simulated():
    pass