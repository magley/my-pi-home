import actuators.buzzer as buzzer
from common import SensorConfig


def setup(config: SensorConfig):
    if not config.simulated:
        buzzer.setup(config.pins[0])


def buzz(config: SensorConfig):
    buzzer.do_buzz_simulated() if config.simulated else buzzer.do_buzz(config.pins[0])


def stop_buzz(config: SensorConfig):
    buzzer.stop_buzz_simulated() if config.simulated else buzzer.stop_buzz(config.pins[0])
