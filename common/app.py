import enum
from common.event import MyPiEvent
from common.config import Config
from common.print_thread import PrintThread


class AppType(enum.Enum):
    GUI = enum.auto()
    CLI = enum.auto()


class App:
    type: AppType
    config: Config
    configs_colors: dict[str, str]
    print_thread: PrintThread
    event: MyPiEvent


    def __init__(self, type: AppType, config: Config):
        self.type = type
        self.config = config
        self.configs_colors = {}
        self.print_thread = PrintThread()
        self.event = MyPiEvent()


    def run(self):
        self.print_thread.start()
        from common.setup import setup_devices, start_event_thread
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
    

    def room_buzzer_on(self):
        self.event.set_buzz_event(self.config.devices['DB'], True)


    def room_buzzer_off(self):
        self.event.set_buzz_event(self.config.devices['DB'], False)


    def door_light_on(self):
        self.event.set_led_event(self.config.devices['DL'], True)


    def door_light_off(self):
        self.event.set_led_event(self.config.devices['DL'], False)


    def cleanup(self):
        import common.setup
        common.setup.cleanup_devices()
