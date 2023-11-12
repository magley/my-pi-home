from enum import Enum, auto
from threading import Thread, Event
import dataclasses
import json
from queue import Queue


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
        self.event = Event()
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
        """

        self.event.clear()


    def wait(self):
        return self.event.wait()


class PrintThread():
    thread: Thread
    queue: Queue
    is_unpaused: Event

    def __init__(self):
        self.thread = Thread(target=self._print_thread, daemon=True)
        self.queue = Queue()
        self.is_unpaused = Event()


    def start(self):
        self.thread.start()


    def _print_thread(self):
        while True:
            if self.is_unpaused.wait():
                item = self.queue.get()
                if not self.is_unpaused.is_set():
                    # Got paused since last get - handle item when we unpause
                    self.queue.put(item)
                else:
                    print(item)


    def put(self, item: str, ignore_paused = False):
        # Ignore puts while we're not listening to stdout
        if self.is_unpaused.is_set() or ignore_paused:
            self.queue.put(item)


    def set_paused(self):
        self.is_unpaused.clear()


    def set_unpaused(self):
        self.is_unpaused.set()
