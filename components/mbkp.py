from util.common import SensorConfig
import typing
import time
import functools
import sensors.mbkp as mbkp


def run(config: SensorConfig, on_read: typing.Callable[[SensorConfig, str], None]):
    reader = _get_reader(config)
    while True:
        reading = reader()
        on_read(config, reading)
        time.sleep(config.read_interval)


def _get_reader(config: SensorConfig):
    if not config.simulated:
        return functools.partial(mbkp.read, output_pins=mbkp.OutputPins(*config.pins[0:4]), input_pins=mbkp.InputPins(*config.pins[4:]))
    else:
        return mbkp.read_simulator
