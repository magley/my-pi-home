from enum import Enum
import threading

class MyPiEventType(Enum):
    STOP = 0,
    BUZZ = 1,


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
        self.type: MyPiEventType = MyPiEventType.STOP
        self.event = threading.Event()


    def set(self, type: MyPiEventType):
        """
        Set the event to a given type and fire the event.

        See also the higher-level API `set_*` functions for specific event types.  
        """
        self.type = type
        self.event.set()


    def set_stop_event(self):
        """
        Set the event that stops all threads from running.
        """
        self.type = MyPiEventType.STOP
        self.event.set()


    def is_set(self) -> bool:
        return self.event.is_set()
    

    def is_set(self, type: MyPiEventType) -> bool:
        """
        Shorthand for `event.is_set() and event.type == type`
        """

        return self.event.is_set() and self.type == type