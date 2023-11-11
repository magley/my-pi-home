from config import SensorConfig
from common import MyPiEvent, MyPiEventType
import typing
import time
import functools
import sensors.mbkp as mbkp


def run(config: SensorConfig, event: MyPiEvent, on_read: typing.Callable[[str], None]):
    reader = _get_reader(config)
    while True:
        if event.is_set(MyPiEventType.STOP):
            print('Stopping mbkp loop')
            break
        reading = reader()
        on_read(reading)
        time.sleep(config.read_interval)


def _get_reader(config: SensorConfig):
    if not config.simulated:
        return functools.partial(mbkp.read, output_pins=mbkp.OutputPins(*config.pins[0:4]), input_pins=mbkp.InputPins(*config.pins[4:]))
    else:
        return mbkp.read_simulator
