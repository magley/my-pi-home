from util.common import load_configs
import argparse
import typing
from util.app import AppType, App


class Args(typing.NamedTuple):
    configs_path: str
    app_type: AppType


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--configs-path', default='data/configs.json')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--gui', action='store_const', dest='app_type', const='gui', default='gui')
    group.add_argument('--cli', action='store_const', dest='app_type', const='cli')
    args = parser.parse_args()
    app_type = AppType.CLI if args.app_type == 'cli' else AppType.GUI
    return Args(args.configs_path, app_type)


def main():
    args = parse_args()
    configs = load_configs(args.configs_path)
    app = App(args.app_type, configs)
    app.run()


if __name__ == '__main__':
    main()
