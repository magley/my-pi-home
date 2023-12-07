from enum import Enum, auto
from threading import Event
from common.config import DeviceConfig


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
        self.cfg: DeviceConfig
        self.event = Event()


    def set(self, type: MyPiEventType):
        """
        Set the event to a given type and fire the event.

        See also the higher-level API `set_*` functions for specific event types.  
        """
        self.type = type
        self.event.set()


    def set_buzz_event(self, cfg: DeviceConfig, do_buzz: bool):
        self.type = MyPiEventType.BUZZ if do_buzz else MyPiEventType.STOP_BUZZ
        self.cfg = cfg
        self.event.set()


    def set_led_event(self, cfg: DeviceConfig, turn_on: bool):
        self.type = MyPiEventType.LED_ON if turn_on else MyPiEventType.LED_OFF
        self.cfg = cfg
        self.event.set()
    

    def consume(self):
        """
        Consume the event, thus making it "unset".
        """

        self.event.clear()


    def wait(self):
        return self.event.wait()
