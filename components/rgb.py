import RPi.GPIO as GPIO
from common.mqtt import MqttSender, build_payload


class RGB_Mqtt(MqttSender):
    def __init__(self, config: dict):
        super().__init__(config)
        self.topic = "iot/rgb"


    # Actuactor can have multiple events, so pass the event as well
    def put(self, cfg: dict, data: dict, event: str):
        if cfg['type'] != 'rgb':
            return

        payload = build_payload(cfg, data, event)
        self.do_put(payload)


def setup(red_pin: int, green_pin: int, blue_pin: int, is_simulated: bool):
    if is_simulated:
        return
    GPIO.setup(red_pin, GPIO.OUT)
    GPIO.setup(green_pin, GPIO.OUT)
    GPIO.setup(blue_pin, GPIO.OUT)


def get_set_color(cfg: dict):
    if cfg['simulated']:
        return set_color_simulated
    return set_color


def set_color(color: str, red_pin: int, green_pin: int, blue_pin: int):
    """
    color is in format (0|1)(0|1)(0|1) (examples: "101", "110", "001")
    """
    GPIO.output(red_pin, _component_to_gpio_signal(color[0]))
    GPIO.output(green_pin, _component_to_gpio_signal(color[1]))
    GPIO.output(blue_pin, _component_to_gpio_signal(color[2]))


def _component_to_gpio_signal(color_component: str):
    return GPIO.LOW if color_component == '0' else GPIO.HIGH


def set_color_simulated(color: str, red_pin: int, green_pin: int, blue_pin: int):
    pass
