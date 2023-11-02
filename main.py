import threading
import time
import config
import util.dht
import argparse
import typing
import RPi.GPIO as GPIO


class Args(typing.NamedTuple):
    configs_path: str
    main_loop_sleep: int


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--configs-path', default='data/configs.json')
    parser.add_argument('--main-loop-sleep', default=1, type=int)
    args = parser.parse_args()
    return Args(args.configs_path, args.main_loop_sleep)


def make_component_loop_threads(args: Args, stop_event: threading.Event):
    configs = config.load_configs(args.configs_path)
    threads: list[threading.Thread] = []
    make_thread = lambda target, *args: threading.Thread(target=target, args=args)
    threads.append(make_thread(util.dht.start_reader_loop, configs[0], stop_event))
    return threads


def start_main_loop(args: Args):
    stop_event = threading.Event()
    threads = make_component_loop_threads(args, stop_event)
    GPIO.setmode(GPIO.BCM)
    try:
        for thread in threads:
            thread.start()
        while True:
            time.sleep(args.main_loop_sleep)
    except KeyboardInterrupt:
        print('Setting stop event...')
        stop_event.set()


def main():
    args = parse_args()
    start_main_loop(args)


if __name__ == '__main__':
    main()
