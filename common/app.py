import enum
import threading
import time
import typing
from common.event import MyPiEvent, MyPiEventType
from common.print_thread import PrintThread
import RPi.GPIO as GPIO
import common.colorizer as colorizer


from components import buzzer, dht, led, mbkp, mds, pir, uds


class AppType(enum.Enum):
    GUI = enum.auto()
    CLI = enum.auto()


class App:
    def __init__(self, type: AppType, config: dict):
        self.type = type
        self.config = config
        self.configs_colors = {}
        self.print_thread = PrintThread()
        self.event = MyPiEvent()
        self._on_read_funcs = []
        self._on_event_funcs = {}

        self.add_on_read_func(self._log_read)


    def _log_read(self, device_cfg: dict, reading: dict):
        t = time.localtime()
        tstr = time.strftime("%H:%M:%S", t)
        dname = str.ljust(device_cfg["name"], 8)
        dtype = str.ljust(device_cfg["type"], 8)
        dpi = str.ljust(device_cfg["runs_on"], 5)
        ss = f'[{tstr}] {dname} [{dtype}] @ {dpi}:\t{reading}'

        available_colors = colorizer.available_colors()
        types = list(set(cfg["type"] for cfg in self.config["devices"]))
        col_index = types.index(device_cfg["type"])
        col = available_colors[col_index]

        self.print_thread.put(ss, col)

    def _log_event(self, device_cfg: dict, type: MyPiEventType):
        t = time.localtime()
        tstr = time.strftime("%H:%M:%S", t)
        dname = str.ljust(device_cfg["name"], 8)
        dtype = str.ljust(device_cfg["type"], 8)
        dpi = str.ljust(device_cfg["runs_on"], 5)
        ss = f'[{tstr}] {dname} [{dtype}] @ {dpi}:\t{type}'

        available_colors = colorizer.available_colors()
        types = list(set(cfg["type"] for cfg in self.config["devices"]))
        col_index = types.index(device_cfg["type"])
        col = available_colors[col_index]

        self.print_thread.put(ss, col, True)


    def add_on_read_func(self, f: typing.Callable):
        """
        Desc
        ---

        Add a function `f(device_cfg: dict, reading: dict) -> None` to a list of
        functions that get called when **any** sensor reads a new value.
        """

        self._on_read_funcs.append(f)
    

    def add_on_event_func(self, type: str, f: typing.Callable):
        """
        Desc
        ---

        Add a function `f(device_cfg: dict, data: dict, event: str) -> None` to a list of
        functions that get called when the actuator of specified type has an event triggered.
        """
        if not self._on_event_funcs.get(type):
            self._on_event_funcs[type] = [f]
        else:    
            self._on_event_funcs[type].append(f)


    def run(self):
        self.print_thread.start()
        self.setup_devices()
        self.start_device_runners()
        self.start_event_thread()
        try:
            self._run()
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()


    def cleanup(self):
        GPIO.cleanup()


    def start_event_thread(self):
        def event_func():
            while True:
                if self.event.wait():
                    type = self.event.type
                    cfg = self.event.cfg
                    from common.event import MyPiEventType

                    if type == MyPiEventType.EMPTY:
                        raise Exception('We should not see the EMPTY event.')
                    if type == MyPiEventType.BUZZ:
                        buzzer.get_do_buzz(cfg)()
                        self.invoke_event_funcs(cfg, {"buzz": 1}, "buzz")
                    elif type == MyPiEventType.STOP_BUZZ:
                        buzzer.get_stop_buzz(cfg)()
                        self.invoke_event_funcs(cfg, {"buzz": 0}, "buzz")
                    elif type == MyPiEventType.LED_ON:
                        led.get_turn_on(cfg)()
                        self.invoke_event_funcs(cfg, {"switch": 1}, "switch")
                    elif type == MyPiEventType.LED_OFF:
                        led.get_turn_off(cfg)()
                        self.invoke_event_funcs(cfg, {"switch": 0}, "switch")
                    else:
                        raise Exception(f'Unsupported Event type: {type}')
                    
                    self._log_event(cfg, type)
                    self.event.consume()


        threading.Thread(target=event_func, args=(), daemon=True).start()


    def _run(self):
        import ui.gui as gui
        import ui.cli as cli

        if self.type == AppType.GUI:
            try:
                gui.gui_app(self)
            except KeyboardInterrupt as e:
                raise e
            except Exception:
                print("Could not start GUI app. Fallback to console app...")
                cli.console_app(self)
        elif self.type == AppType.CLI:
            cli.console_app(self)
        else:
            raise Exception('Unknown app type')
        

    def get_device_by_code(self, code: str) -> dict:
        for cfg in self.config['devices']:
            if cfg['name'] == code:
                return cfg
        raise Exception(f"Could not find device:{code}")
    

    def room_buzzer_on(self):
        self.event.set_buzz_event(self.get_device_by_code('DB'), True)


    def room_buzzer_off(self):
        self.event.set_buzz_event(self.get_device_by_code('DB'), False)


    def door_light_on(self):
        self.event.set_led_event(self.get_device_by_code('DL'), True)


    def door_light_off(self):
        self.event.set_led_event(self.get_device_by_code('DL'), False)


    def setup_devices(self):
        GPIO.setmode(GPIO.BCM)

        for device_cfg in self.config['devices']:
            pin = device_cfg['pins'][0]
            
            if device_cfg['type'] == 'dht':
                dht.setup(pin)
            elif device_cfg['type'] == 'pir':
                # https://docs.python.org/3/faq/programming.html#why-do-lambdas-defined-in-a-loop-with-different-values-all-return-the-same-result
                # Can't do `lambda: self.invoke_read_funcs(device_cfg, {})`
                # because lambda closures do not capture by default.
                pir.setup(device_cfg['pins'][0], device_cfg['simulated'], lambda cfg=device_cfg: self.invoke_read_funcs(cfg, pir._reading()))
            elif device_cfg['type'] == 'buzzer':
                buzzer.setup(pin)
            elif device_cfg['type'] == 'mds':
                mds.setup(pin)
            elif device_cfg['type'] == 'led':
                led.setup(pin)
            elif device_cfg['type'] == 'uds':
                uds.setup(device_cfg['pins'][0], device_cfg['pins'][1])
            elif device_cfg['type'] == 'mbkp':
                mbkp.setup(device_cfg['pins'][:4], device_cfg['pins'][4:])    
            else:
                raise Exception(f'Could not setup device for type {device_cfg["type"]}.\nDid you forget to include an else-if?')


    def invoke_read_funcs(self, device_cfg: dict, reading: dict):
        for func in self._on_read_funcs:
            func(device_cfg, reading)


    def invoke_event_funcs(self, device_cfg: dict, data: dict, event: str):
        for func in self._on_event_funcs[device_cfg['type']]:
            func(device_cfg, data, event)


    def start_device_runners(self):
        def reader_loop(device_cfg: dict, get_reader_func: typing.Callable):
            reader_func = get_reader_func(device_cfg)
            while True:
                reading = reader_func()
                self.invoke_read_funcs(device_cfg, reading)
                time.sleep(device_cfg['read_interval'])


        def start_reader(device_cfg: dict, get_reader_func: typing.Callable):
            args = [device_cfg, get_reader_func]
            threading.Thread(target = reader_loop, args=args, daemon=True).start()


        for device_cfg in self.config['devices']:
            if device_cfg['type'] == 'dht':
                start_reader(device_cfg, dht.get_reader_func)
            elif device_cfg['type'] == 'pir':
                pass # Pir doesn't have a 'read', it uses its own thread.
            elif device_cfg['type'] == 'buzzer':
                pass # Actuator doesn't have a reader.
            elif device_cfg['type'] == 'mds':
                start_reader(device_cfg, mds.get_reader_func) 
            elif device_cfg['type'] == 'led':
                pass # Actuator doesn't have a reader.
            elif device_cfg['type'] == 'uds':
                start_reader(device_cfg, uds.get_reader_func)
            elif device_cfg['type'] == 'mbkp':
                start_reader(device_cfg, mbkp.get_reader_func)
            else:
                raise Exception(f'Could not start device runner for type {device_cfg["type"]}.\nDid you forget to include an else-if?')