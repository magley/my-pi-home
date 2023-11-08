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


def make_component_loop_threads(configs: dict[str, config.SensorConfig], event: MyPiEvent) -> list[threading.Thread]:
    '''
    Desc
    ----
    Read all devices in the config file and create the appropriate threads.

    Return
    ------
    A list containing all the created threads.

    Each thread's runnable is a `run` method for a device component.
    '''

    lock = threading.Lock()

    def make_thread(target: typing.Callable, *args):
        return threading.Thread(target=target, args=args)

    def rpir1_on_motion():
        with lock:
            print(f"{time.strftime('%H:%M:%S', time.localtime())} RPIR1 motion")

    def rpir2_on_motion():
        with lock:
            print(f"{time.strftime('%H:%M:%S', time.localtime())} RPIR2 motion")

    threads: list[threading.Thread] = []
    threads.append(make_thread(dht.run, configs['RDHT1'], event, lock))
    threads.append(make_thread(dht.run, configs['RDHT2'], event, lock))
    threads.append(make_thread(pir.run, configs['RPIR1'], event, lock, rpir1_on_motion))
    threads.append(make_thread(pir.run, configs['RPIR2'], event, lock, rpir2_on_motion))
    threads.append(make_thread(buzzer.run, configs['DB'], event, lock))

    return threads


def main():
    args = parse_args()

    event = MyPiEvent()
    configs = config.load_configs(args.configs_path)
    threads = make_component_loop_threads(configs, event)
    GPIO.setmode(GPIO.BCM)

    try:
        for thread in threads:
            thread.start()

        time.sleep(5)
        event.set_buzz_event(configs['DB'].pin, True)
        time.sleep(5)
        event.set_buzz_event(configs['DB'].pin, False)
        time.sleep(1)
        event.set_buzz_event(configs['DB'].pin, True)

        while True:   
            time.sleep(args.main_loop_sleep)

    except KeyboardInterrupt:
        print('Setting stop event...')
        event.set_stop_event()


if __name__ == '__main__':
    main()
