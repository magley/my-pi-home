import asyncio
import config
import util.dht
import argparse
import typing
import RPi.GPIO as GPIO

class Args(typing.NamedTuple):
    configs_path: str


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-configs_path', default='data/configs.json')
    args = parser.parse_args()
    return Args(args.configs_path)


def event_loop(args: Args):
    configs = config.load_configs(args.configs_path)
    loop = asyncio.get_event_loop()
    # NOTE: Here is where we will add the other runners
    loop.create_task(util.dht.start_runner(configs[0]))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass


def main():
    args = parse_args()
    # FIXME: This is a global and will probably lead to trouble in parallel execution
    #        Same problem exists in the sample skeleton as well, no?
    #        Also it's ugly for it to be here
    GPIO.setmode(GPIO.BCM)
    event_loop(args)


if __name__ == '__main__':
    main()
