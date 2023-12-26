from common.config import load_configs
import argparse
import typing
from common.app import App
from components.dht import DHT_Mqtt
from components.lcd import LCD_Mqtt
from components.pir import PIR_Mqtt
from components.uds import UDS_Mqtt
from components.mds import MDS_Mqtt
from components.mbkp import MBKP_Mqtt
from components.buzzer import Buzzer_Mqtt
from components.led import LED_Mqtt
from components.gyro import Gyro_Mqtt
from common.app_logic import read_GDHT_to_GLCD, on_DPIR_movement_turn_on_DL_for10s


class Args(typing.NamedTuple):
    configs_path: str
    pi: int


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--configs-path', default='data/configs.json')
    parser.add_argument('--pi', default=1)
    args = parser.parse_args()
    return Args(args.configs_path, args.pi)


def main():
    args = parse_args()
    configs = load_configs(args.configs_path)
    app = App(configs, args.pi)

    dht_mqtt = DHT_Mqtt(configs)
    pir_mqtt = PIR_Mqtt(configs)
    uds_mqtt = UDS_Mqtt(configs)
    mds_mqtt = MDS_Mqtt(configs)
    mbkp_mqtt = MBKP_Mqtt(configs)
    buzzer_mqtt = Buzzer_Mqtt(configs)
    led_mqtt = LED_Mqtt(configs)
    lcd_mqtt = LCD_Mqtt(configs)
    gyro_mqtt = Gyro_Mqtt(configs)

    app.add_on_read_func(dht_mqtt.put)
    app.add_on_read_func(pir_mqtt.put)
    app.add_on_read_func(uds_mqtt.put)
    app.add_on_read_func(mds_mqtt.put)
    app.add_on_read_func(mbkp_mqtt.put)
    app.add_on_read_func(gyro_mqtt.put)
    app.add_on_event_func('buzzer', buzzer_mqtt.put)
    app.add_on_event_func('led', led_mqtt.put)
    app.add_on_event_func('lcd', lcd_mqtt.put)

    app.add_on_read_func(read_GDHT_to_GLCD(app))
    app.add_on_read_func(on_DPIR_movement_turn_on_DL_for10s(app))
    app.run()

if __name__ == '__main__':
    main()
