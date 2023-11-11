import threading
import time
from common import MyPiEvent, MyPiEventType
import config
import argparse
import typing
import RPi.GPIO as GPIO
from components import dht
from components import pir
from components import buzzer
from components import mds
from components import led
from components import uds
from components import mbkp
from sensors.dht import DHTReading
from sensors.uds import UDSReading, UDSCode

class Args(typing.NamedTuple):
    configs_path: str
    main_loop_sleep: int


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--configs-path', default='data/configs.json')
    parser.add_argument('--main-loop-sleep', default=1, type=int)
    args = parser.parse_args()
    return Args(args.configs_path, args.main_loop_sleep)


def setup_components(configs: dict[str, config.SensorConfig], print_lock: threading.Lock):
    def make_thread(target: typing.Callable, *args):
        return threading.Thread(target=target, args=args, daemon=True)

    def pir_on_motion(name: str):
        with print_lock:
            print(f"{time.strftime('%H:%M:%S', time.localtime())} {name} motion")

    def mds_on_read(name: str, val: int):
        with print_lock:
            print(f"{time.strftime('%H:%M:%S', time.localtime())} {name} {val}")
    
    def dht_on_read(name: str, reading: DHTReading):
        t = time.localtime()
        with print_lock:
            print(f"{time.strftime('%H:%M:%S', t)} {name} {reading.humidity}% {reading.temperature}°C")

    def uds_on_read(name: str, reading: UDSReading):
        t = time.localtime()
        with print_lock:
            val = 'Timed out' if reading.code == UDSCode.TIMED_OUT else f"{reading.distance_in_cm}cm"
            print(f"{time.strftime('%H:%M:%S', t)} {name} {val}")

    def mbkp_on_read(name: str, val: str):
        t = time.localtime()
        if val == '':
            return
        with print_lock:
            print(f"{time.strftime('%H:%M:%S', t)} {name} {val}")

    for cfg in configs.values():
        match cfg.type:
            case 'dht':
                make_thread(dht.run, cfg, lambda val: dht_on_read(cfg.name, val)).start()
            case 'pir':
                pir.setup(cfg, lambda: pir_on_motion(cfg.name))
            case 'buzzer':
                buzzer.setup(cfg)
            case 'mds':
                make_thread(mds.run, cfg, lambda val: mds_on_read(cfg.name, val))
            case 'led':
                led.setup(cfg)
            case 'uds':
                make_thread(uds.run, cfg, lambda val: uds_on_read(cfg.name, val)).start()
            case 'mbkp':
                make_thread(mbkp.run, cfg, lambda val: mbkp_on_read(cfg.name, val)).start()
            case _:
                raise Exception('Unknown config type')


def console_app(event: MyPiEvent, configs: dict[str, config.SensorConfig], args: Args, print_lock: threading.Lock):
    try:
        while True:
            try:
                print_lock.release()
            except:
                pass

            print_lock.acquire()
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
                event.set_buzz_event(configs['DB'], True)
            elif i == 'room-buzz-off':
                event.set_buzz_event(configs['DB'], False)
            elif i == 'door-light-on':
                event.set_led_event(configs['DL'], True)
            elif i == 'door-light-off':
                event.set_led_event(configs['DL'], False)
            elif i == 'listen':
                print_lock.release()
                try:
                    while True:
                        time.sleep(args.main_loop_sleep)
                except KeyboardInterrupt:
                    print("Stopped listening...")
            elif i == 'quit':
                break
            else:
                print("Unknown command")
            
    except KeyboardInterrupt:
        pass
    finally:
        try:
            print_lock.release()
        except:
            pass


def gui_app(event: MyPiEvent, configs: dict[str, config.SensorConfig], args: Args, print_lock: threading.Lock):
    err = False
    try:
        from guizero import App, Text, PushButton

        def room_buzzer_on():
            event.set_buzz_event(configs['DB'], True)

        def room_buzzer_off():
            event.set_buzz_event(configs['DB'], False)

        def door_light_on():
            event.set_led_event(configs['DL'], True)

        def door_light_off():
            event.set_led_event(configs['DL'], False)


        app = App(title="my pi home gui")
        PushButton(app, text="Toggle buzzer on", command=room_buzzer_on)
        PushButton(app, text="Toggle buzzer off", command=room_buzzer_off)
        PushButton(app, text="Door light on", command=door_light_on)
        PushButton(app, text="Door light off", command=door_light_off)

        app.display()
    except Exception:
        print("Could not start GUI app. Fallback to console app...")
        err = True

    if err:
        console_app(event, configs, args, print_lock)


def event_thread(event: MyPiEvent, print_lock):
    while True:
        if event.wait():
            match event.type:
                case MyPiEventType.EMPTY:
                    raise Exception('We should not see the EMPTY event.')
                case MyPiEventType.BUZZ:
                    cfg = event.sensor
                    buzzer.buzz(cfg)
                    with print_lock:
                        print(f"{time.strftime('%H:%M:%S', time.localtime())} Start buzzing on pin {cfg.pins[0]}")
                case MyPiEventType.STOP_BUZZ:
                    cfg = event.sensor
                    buzzer.stop_buzz(cfg)
                    with print_lock:
                        print(f"{time.strftime('%H:%M:%S', time.localtime())} Stop buzzing on pin {cfg.pins[0]}")
                case MyPiEventType.LED_ON:
                    cfg = event.sensor
                    led.turn_on(cfg)
                    with print_lock:
                        print(f"{time.strftime('%H:%M:%S', time.localtime())} Turn on LED on pin {cfg.pins[0]}")
                case MyPiEventType.LED_OFF:
                    cfg = event.sensor
                    led.turn_off(cfg)
                    with print_lock:
                        print(f"{time.strftime('%H:%M:%S', time.localtime())} Turn off LED on pin {cfg.pins[0]}")
                case _:
                    raise Exception('Unknown event type')
            event.consume()


def main():
    args = parse_args()
    configs = config.load_configs(args.configs_path)
    print_lock = threading.Lock()
    GPIO.setmode(GPIO.BCM)
    setup_components(configs, print_lock)

    event = MyPiEvent()
    threading.Thread(target=event_thread, args=(event, print_lock), daemon=True).start()
    gui_app(event, configs, args, print_lock)


if __name__ == '__main__':
    main()
