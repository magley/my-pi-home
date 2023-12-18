from common.config import load_configs
import argparse
import typing
from common.app import AppType, App
from components.dht import DHT_Mqtt
from components.pir import PIR_Mqtt
from components.uds import UDS_Mqtt
from components.mds import MDS_Mqtt
from components.mbkp import MBKP_Mqtt
from components.buzzer import Buzzer_Mqtt


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

    dht_mqtt = DHT_Mqtt(configs)
    pir_mqtt = PIR_Mqtt(configs)
    uds_mqtt = UDS_Mqtt(configs)
    mds_mqtt = MDS_Mqtt(configs)
    mbkp_mqtt = MBKP_Mqtt(configs)
    buzzer_mqtt = Buzzer_Mqtt(configs)

    app.add_on_read_func(dht_mqtt.put)
    app.add_on_read_func(pir_mqtt.put)
    app.add_on_read_func(uds_mqtt.put)
    app.add_on_read_func(mds_mqtt.put)
    app.add_on_read_func(mbkp_mqtt.put)
    app.add_on_event_func('buzzer', buzzer_mqtt.put)
    app.run()

if __name__ == '__main__':
    main()
