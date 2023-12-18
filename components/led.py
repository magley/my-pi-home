from RPi import GPIO
from common.mqtt import MqttSender, build_payload


class LED_Mqtt(MqttSender):
    def __init__(self, config: dict):
        super().__init__(config)
        self.topic = "iot/led"


    # Actuactor can have multiple events, so pass the event as well
    def put(self, cfg: dict, data: dict, event: str):
        if cfg['type'] != 'led':
            return

        buzz_payload = build_payload(cfg, data, event)
        self.do_put(buzz_payload)


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