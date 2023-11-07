import threading
import time
import config
import argparse
import typing
import RPi.GPIO as GPIO
from components import dht
from components import pir


class Args(typing.NamedTuple):
    configs_path: str
    main_loop_sleep: int


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--configs-path', default='data/configs.json')
    parser.add_argument('--main-loop-sleep', default=1, type=int)
    args = parser.parse_args()
    return Args(args.configs_path, args.main_loop_sleep)


def make_component_loop_threads(configs: list[config.SensorConfig], stop_event: threading.Event) -> list[threading.Thread]:
    '''
    Desc
    ----
    Read all devices in the config file and create the appropriate threads.

    Return
    ------
    A list containing all the created threads.

    Each thread's runnable is a `run` method for a device component.
    '''

    threads: list[threading.Thread] = []
    make_thread = lambda target, *args: threading.Thread(target=target, args=args)
    lock = threading.Lock()

    for cfg in configs:
        func = get_device_run_loop_func(cfg.type)
        threads.append(make_thread(func, cfg, stop_event, lock))

    return threads


def get_device_run_loop_func(type: str) -> typing.Callable:
    '''
    Desc
    ----
    Given a `type` (as defined in the config file), return the appropriate device `run` method.

    The method should decide whether to run the simulator or communicate with the rPi.

    The method will run in its own thread.

    The method should loop until a stop event is received.
    '''
    
    map = {''
        'dht': dht.run,
        'pir': pir.run,
    }

    return map[type]


def main():
    args = parse_args()
    stop_event = threading.Event()
    configs = config.load_configs(args.configs_path)
    threads = make_component_loop_threads(configs, stop_event)
    GPIO.setmode(GPIO.BCM)

    try:
        for thread in threads:
            thread.start()
        while True:
            time.sleep(args.main_loop_sleep)
    except KeyboardInterrupt:
        print('Setting stop event...')
        stop_event.set()


if __name__ == '__main__':
    main()
