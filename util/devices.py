from util.common import SensorConfig
from typing import TypeVar, Callable
import time
import actuators.buzzer as buzzer
import actuators.led as led
import sensors.dht as dht
import sensors.mbkp as mbkp
import sensors.mds as mds
import sensors.pir as pir
import sensors.uds as uds


T = TypeVar('T')


def run_reader(config: SensorConfig,
               get_reader: Callable[[SensorConfig], Callable[[], T]],
               on_read: Callable[[SensorConfig, T], None]):
    reader = get_reader(config)
    while True:
        reading = reader()
        on_read(config, reading)
        time.sleep(config.read_interval)


def buzzer_setup(config: SensorConfig):
    if not config.simulated:
        buzzer.setup(config.pins[0])


def buzzer_buzz(config: SensorConfig):
    buzzer.do_buzz_simulated() if config.simulated else buzzer.do_buzz(config.pins[0])


def buzzer_stop_buzz(config: SensorConfig):
    buzzer.stop_buzz_simulated() if config.simulated else buzzer.stop_buzz(config.pins[0])


def dht_get_reader(config: SensorConfig):
    if not config.simulated:
        return lambda: dht.read_dht(config.pins[0])
    else:
        return dht.Simulator().read_dht


def led_setup(config: SensorConfig):
    if not config.simulated:
        led.setup(config.pins[0])


def led_turn_on(config: SensorConfig):
    led.turn_on_simulated() if config.simulated else led.turn_on(config.pins[0])


def led_turn_off(config: SensorConfig):
    led.turn_off_simulated() if config.simulated else led.turn_off(config.pins[0])


def mbkp_get_reader(config: SensorConfig):
    if not config.simulated:
        return lambda: mbkp.read(mbkp.OutputPins(*config.pins[0:4]), input_pins=mbkp.InputPins(*config.pins[4:]))
    else:
        return mbkp.read_simulator


def mds_get_reader(config: SensorConfig):
    if not config.simulated:
        return lambda: mds.read(config.pins[0])
    else:
        return mds.read_simulator


def pir_setup(config: SensorConfig, when_motion: Callable[[SensorConfig], None]):
    if not config.simulated:
        pir.setup(config.pins[0], lambda: when_motion(config))
    else:
        pir.setup_simulator(lambda: when_motion(config))


def uds_get_reader(config: SensorConfig):
    if not config.simulated:
        return lambda: uds.read(config.pins[0], config.pins[1])
    else:
        return uds.read_simulator
