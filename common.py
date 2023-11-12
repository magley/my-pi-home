from enum import Enum, auto
import threading
import dataclasses
import json


@dataclasses.dataclass
class SensorConfig:
    name: str
    type: str
    pins: list[int]
    simulated: bool
    read_interval: float


def load_configs(path):
    list_of_dict = json.load(open(path))
    res = {
        x['name']: SensorConfig(**x) for x in list_of_dict
    }

    return res


class MyPiEventType(Enum):
    EMPTY = auto()
    BUZZ = auto(),
    STOP_BUZZ = auto(),
    LED_ON = auto(),
    LED_OFF = auto()


class MyPiEvent():
    """
    Thin adapter for `threading.Event` with custom parameters. There should be
    at most one instance of this class, and all event-related logic should use
    that instance.

    Individual threads may query the event type using `type` or `is_set(type)`.

    Other vars are type-related and should be read from only if the appropriate
    event was set.

    Think of `MyPiEvent` as a C `union`.
    """

    def __init__(self):
        self.type: MyPiEventType = MyPiEventType.EMPTY
        self.event = threading.Event()
        self.sensor: SensorConfig


    def set(self, type: MyPiEventType):
        """
        Set the event to a given type and fire the event.

        See also the higher-level API `set_*` functions for specific event types.  
        """
        self.type = type
        self.event.set()


    def set_buzz_event(self, sensor: SensorConfig, do_buzz: bool):
        self.type = MyPiEventType.BUZZ if do_buzz else MyPiEventType.STOP_BUZZ
        self.sensor = sensor
        self.event.set()


    def set_led_event(self, sensor: SensorConfig, turn_on: bool):
        self.type = MyPiEventType.LED_ON if turn_on else MyPiEventType.LED_OFF
        self.sensor = sensor
        self.event.set()
    

    def consume(self):
        """
        Consume the event, thus making it "unset".

        Use this for events that only a single device should respond to, like
        a buzzer. 
        Events such as `STOP` should be handled by all threads and therefore
        should never be "consumed".
        """

        self.event.clear()


    def wait(self):
        return self.event.wait()
