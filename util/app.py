import enum
from util.common import MyPiEvent, SensorConfig, PrintThread


class AppType(enum.Enum):
    GUI = enum.auto()
    CLI = enum.auto()


class App:
    type: AppType
    configs: dict[str, SensorConfig]
    print_thread: PrintThread
    event: MyPiEvent


    def __init__(self, type: AppType, configs: dict[str, SensorConfig]):
        self.type = type
        self.configs = configs
        self.print_thread = PrintThread()
        self.event = MyPiEvent()


    def run(self):
        self.print_thread.start()
        from util.setup import setup_devices, start_event_thread
        setup_devices(self)
        start_event_thread(self)
        try:
            self._run()
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()


    def _run(self):
        import ui.gui as gui
        import ui.cli as cli
        match self.type:
            case AppType.GUI:
                try:
                    gui.gui_app(self)
                except KeyboardInterrupt as e:
                    raise e
                except:
                    print("Could not start GUI app. Fallback to console app...")
                    cli.console_app(self)
            case AppType.CLI:
                cli.console_app(self)
            case _:
                raise Exception('Unknown app type')


    def room_buzzer_on(self):
        self.event.set_buzz_event(self.configs['DB'], True)


    def room_buzzer_off(self):
        self.event.set_buzz_event(self.configs['DB'], False)


    def door_light_on(self):
        self.event.set_led_event(self.configs['DL'], True)


    def door_light_off(self):
        self.event.set_led_event(self.configs['DL'], False)


    def cleanup(self):
        import util.setup
        util.setup.cleanup_devices()
