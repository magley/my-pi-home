import typing
import sensors.pir as pir
from common import SensorConfig

def setup(config: SensorConfig, when_motion: typing.Callable[[SensorConfig], None]):
    if not config.simulated:
        pir.setup(config.pins[0], lambda: when_motion(config))
    else:
        pir.setup_simulator(lambda: when_motion(config))
