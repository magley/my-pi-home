from common.config import DeviceConfig
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


def run_reader(config: DeviceConfig,
               get_reader: Callable[[DeviceConfig], Callable[[], T]],
               on_read: Callable[[DeviceConfig, T], None]):
    reader = get_reader(config)
    while True:
        reading = reader()
        on_read(config, reading)
        time.sleep(config.read_interval)


def buzzer_setup(config: DeviceConfig):
    if not config.simulated:
        buzzer.setup(config.pins[0])


def buzzer_buzz(config: DeviceConfig):
    buzzer.do_buzz_simulated() if config.simulated else buzzer.do_buzz(config.pins[0])


def buzzer_stop_buzz(config: DeviceConfig):
    buzzer.stop_buzz_simulated() if config.simulated else buzzer.stop_buzz(config.pins[0])


def dht_get_reader(config: DeviceConfig):
    if not config.simulated:
        return lambda: dht.read_dht(config.pins[0])
    else:
        return dht.Simulator().read_dht


def led_setup(config: DeviceConfig):
    if not config.simulated:
        led.setup(config.pins[0])


def led_turn_on(config: DeviceConfig):
    led.turn_on_simulated() if config.simulated else led.turn_on(config.pins[0])


def led_turn_off(config: DeviceConfig):
    led.turn_off_simulated() if config.simulated else led.turn_off(config.pins[0])


def mbkp_setup(config: DeviceConfig):
    if not config.simulated:
        mbkp.setup(mbkp.OutputPins(*config.pins[0:4]), mbkp.InputPins(*config.pins[4:]))


def mbkp_get_reader(config: DeviceConfig):
    if not config.simulated:
        return lambda: mbkp.read(mbkp.OutputPins(*config.pins[0:4]), mbkp.InputPins(*config.pins[4:]))
    else:
        return mbkp.read_simulator


def mds_setup(config: DeviceConfig):
    if not config.simulated:
        mds.setup(config.pins[0])


def mds_get_reader(config: DeviceConfig):
    if not config.simulated:
        return lambda: mds.read(config.pins[0])
    else:
        return mds.read_simulator


def pir_setup(config: DeviceConfig, when_motion: Callable[[DeviceConfig], None]):
    if not config.simulated:
        pir.setup(config.pins[0], lambda: when_motion(config))
    else:
        pir.setup_simulator(lambda: when_motion(config))


def uds_setup(config: DeviceConfig):
    if not config.simulated:
        uds.setup(config.pins[0], config.pins[1])


def uds_get_reader(config: DeviceConfig):
    if not config.simulated:
        return lambda: uds.read(config.pins[0], config.pins[1])
    else:
        return uds.read_simulator
