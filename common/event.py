from enum import Enum, auto
from threading import Event, Lock


class MyPiEventType(Enum):
    EMPTY = auto()
    BUZZ = auto(),
    STOP_BUZZ = auto(),
    LED_ON = auto(),
    LED_OFF = auto(),
    LCD_WRITE = auto(),
    DEBUG_GSG_SHAKE = auto(),
    D4S7_WRITE = auto(),
    D4S7_BLANK = auto(),
    RGB_COLOR = auto()


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
        self.cfg = {} # Configuration for the device whose event is being fired.
        self.payload = None # Payload for the event, if any.
        # MyPiEvent instance is accessed from multiple threads, so we need to ensure there aren't any
        # data races when setting events.
        self.payload_access_lock = Lock()
        self.event = Event()


    def set(self, type: MyPiEventType):
        """
        Set the event to a given type and fire the event.

        See also the higher-level API `set_*` functions for specific event types.  
        """
        self.payload_access_lock.acquire()
        self.type = type
        self.event.set()


    def set_buzz_event(self, cfg: dict, do_buzz: bool):
        self.payload_access_lock.acquire()
        self.type = MyPiEventType.BUZZ if do_buzz else MyPiEventType.STOP_BUZZ
        self.cfg = cfg
        self.event.set()


    def set_led_event(self, cfg: dict, turn_on: bool):
        self.payload_access_lock.acquire()
        self.type = MyPiEventType.LED_ON if turn_on else MyPiEventType.LED_OFF
        self.cfg = cfg
        self.event.set()


    def set_lcd_event(self, cfg: dict, text_to_write: str):
        self.payload_access_lock.acquire()
        self.type = MyPiEventType.LCD_WRITE
        self.cfg = cfg
        self.payload = text_to_write
        self.event.set()


    def set_debug_gsg_shake_event(self, cfg: dict):
        self.payload_access_lock.acquire()
        self.type = MyPiEventType.DEBUG_GSG_SHAKE
        self.cfg = cfg
        self.event.set()
    
    
    def set_d4s7_write_event(self, cfg: dict, text: str):
        self.payload_access_lock.acquire()
        self.type = MyPiEventType.D4S7_WRITE
        self.cfg = cfg
        self.payload = text
        self.event.set()
    

    def set_d4s7_blank_event(self, cfg: dict):
        self.payload_access_lock.acquire()
        self.type = MyPiEventType.D4S7_BLANK
        self.cfg = cfg
        self.payload = ''
        self.event.set()

    
    def set_rgb_event(self, cfg: dict, color: str):
        self.payload_access_lock.acquire()
        self.type = MyPiEventType.RGB_COLOR
        self.cfg = cfg
        self.payload = color
        self.event.set()


    def consume(self):
        """
        Consume the event, thus making it "unset".
        """

        self.event.clear()
        self.payload_access_lock.release()


    def wait(self):
        return self.event.wait()
