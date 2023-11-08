import threading
import time
from common import MyPiEvent
import config
import argparse
import typing
import RPi.GPIO as GPIO
from components import dht
from components import pir
from components import buzzer


class Args(typing.NamedTuple):
    configs_path: str
    main_loop_sleep: int


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--configs-path', default='data/configs.json')
    parser.add_argument('--main-loop-sleep', default=1, type=int)
    args = parser.parse_args()
    return Args(args.configs_path, args.main_loop_sleep)


def make_component_loop_threads(configs: dict[str, config.SensorConfig], event: MyPiEvent, print_lock: threading.Lock) -> list[threading.Thread]:
    '''
    Desc
    ----
    Read all devices in the config file and create the appropriate threads.

    Return
    ------
    A list containing all the created threads.

    Each thread's runnable is a `run` method for a device component.
    '''

    

    def make_thread(target: typing.Callable, *args):
        return threading.Thread(target=target, args=args)

    def rpir1_on_motion():
        with print_lock:
            print(f"{time.strftime('%H:%M:%S', time.localtime())} RPIR1 motion")

    def rpir2_on_motion():
        with print_lock:
            print(f"{time.strftime('%H:%M:%S', time.localtime())} RPIR2 motion")

    def dpir1_on_motion():
        with print_lock:
            print(f"{time.strftime('%H:%M:%S', time.localtime())} DPIR1 motion")

    threads: list[threading.Thread] = []
    threads.append(make_thread(dht.run, configs['RDHT1'], event, print_lock))
    threads.append(make_thread(dht.run, configs['RDHT2'], event, print_lock))
    threads.append(make_thread(pir.run, configs['RPIR1'], event, print_lock, rpir1_on_motion))
    threads.append(make_thread(pir.run, configs['RPIR2'], event, print_lock, rpir2_on_motion))
    threads.append(make_thread(buzzer.run, configs['DB'], event, print_lock))
    threads.append(make_thread(pir.run, configs['DPIR1'], event, print_lock, dpir1_on_motion))

    return threads


def console_app(threads: list, event: MyPiEvent, configs: dict, args: Args, print_lock: threading.Lock):
    try:
        for thread in threads:
            thread.start()

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
            print('-' * 30)
            print('Enter command:', end='')
            i = input()

            if i == 'room-buzz-on':
                event.set_buzz_event(configs['DB'].pin, True)
            elif i == 'room-buzz-off':
                event.set_buzz_event(configs['DB'].pin, False)
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
        print('Setting stop event...')
        event.set_stop_event()


def gui_app(threads: list, event: MyPiEvent, configs: dict, args: Args, print_lock: threading.Lock):
    err = False
    try:
        from guizero import App, Text, PushButton

        def room_buzzer_on():
            event.set_buzz_event(configs['DB'].pin, True)

        def room_buzzer_off():
            event.set_buzz_event(configs['DB'].pin, False)

        app = App(title="guizero")
        PushButton(app, text="Toggle buzzer on", command=room_buzzer_on)
        PushButton(app, text="Toggle buzzer off", command=room_buzzer_off)

        for thread in threads:
            thread.start()

        app.display()
        event.set_stop_event()
    except Exception:
        print("Could not start GUI app. Fallback to console app...")
        err = True

    if err:
        console_app(threads, event, configs, args, print_lock)


def main():
    args = parse_args()
    event = MyPiEvent()
    configs = config.load_configs(args.configs_path)
    print_lock = threading.Lock()
    threads = make_component_loop_threads(configs, event, print_lock)
    GPIO.setmode(GPIO.BCM)

    gui_app(threads, event, configs, args, print_lock)


if __name__ == '__main__':
    main()
