import actuators.led as led
from util.common import SensorConfig

def setup(config: SensorConfig):
    if not config.simulated:
        led.setup(config.pins[0])


def turn_on(config: SensorConfig):
    led.turn_on_simulated() if config.simulated else led.turn_on(config.pins[0])


def turn_off(config: SensorConfig):
    led.turn_off_simulated() if config.simulated else led.turn_off(config.pins[0])
