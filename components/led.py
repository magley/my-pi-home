import actuators.led as led
import config

def setup(config: config.SensorConfig):
    if not config.simulated:
        led.setup(config.pins[0])


def turn_on(config: config.SensorConfig):
    led.turn_on_simulated() if config.simulated else led.turn_on(config.pins[0])


def turn_off(config: config.SensorConfig):
    led.turn_off_simulated() if config.simulated else led.turn_off(config.pins[0])
