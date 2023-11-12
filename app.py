import threading
import enum
import time
from common import MyPiEvent, SensorConfig


class AppType(enum.Enum):
    GUI = enum.auto()
    CLI = enum.auto()


class App:
    type: AppType
    configs: dict[str, SensorConfig]
    print_lock: threading.Lock
    event: MyPiEvent


    def __init__(self, type: AppType, configs: dict[str, SensorConfig]):
        self.type = type
        self.configs = configs
        self.print_lock = threading.Lock()
        self.event = MyPiEvent()


    def run(self):
        import setup
        setup.setup_devices(self)
        setup.start_event_thread(self)
        try:
            self._run()
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()


    def _run(self):
        match self.type:
            case AppType.GUI:
                try:
                    self.gui_app()
                except KeyboardInterrupt as e:
                    raise e
                except:
                    print("Could not start GUI app. Fallback to console app...")
                    self.console_app()
            case AppType.CLI:
                self.console_app()
            case _:
                raise Exception('Unknown app type')


    def console_app(self):
        done = False
        while not done:
            done = self._console_app()


    def _console_app(self):
        try:
            self.print_lock.release()
        except:
            pass

        self.print_lock.acquire()
        print("\nSelect command")
        print('-' * 30)
        print("listen\t\t(Use keyboard interrupt to return to menu)")
        print('quit')
        print("room-buzz-on")
        print("room-buzz-off")
        print("door-light-on")
        print("door-light-off")
        print('-' * 30)
        print('Enter command:', end='')
        i = input()

        if i == 'room-buzz-on':
            self.room_buzzer_on()
        elif i == 'room-buzz-off':
            self.room_buzzer_off()
        elif i == 'door-light-on':
            self.door_light_on()
        elif i == 'door-light-off':
            self.door_light_off()
        elif i == 'listen':
            self.print_lock.release()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("Stopped listening...")
        elif i == 'quit':
            return True
        else:
            print("Unknown command")

        return False


    def gui_app(self):
        from guizero import App, PushButton
        app = App(title="my pi home gui")
        PushButton(app, text="Toggle buzzer on", command=self.room_buzzer_on)
        PushButton(app, text="Toggle buzzer off", command=self.room_buzzer_off)
        PushButton(app, text="Door light on", command=self.door_light_on)
        PushButton(app, text="Door light off", command=self.door_light_off)
        app.display()


    def room_buzzer_on(self):
        self.event.set_buzz_event(self.configs['DB'], True)


    def room_buzzer_off(self):
        self.event.set_buzz_event(self.configs['DB'], False)


    def door_light_on(self):
        self.event.set_led_event(self.configs['DL'], True)


    def door_light_off(self):
        self.event.set_led_event(self.configs['DL'], False)


    def cleanup(self):
        # FIXME: Is this necessary?
        try:
            self.print_lock.release()
        except:
            pass
