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
from components.gyro import Gyro_Mqtt, debug_shake
from components.d4s7 import D4S7_Mqtt
from common.app_logic import read_GDHT_to_GLCD, on_DPIR_movement_turn_on_DL_for10s, on_DUS_add_userdata, on_DPIR_movement_detect_person_from_DUS, on_PIR_when_no_people_alarm, websocket_if_alarm_then_turn_on_buzzer_else_turn_off_buzzer, on_GSG_motion_add_userdata, on_GSG_motion_check_for_alarm

class Args(typing.NamedTuple):
    configs_path: str
    pi: int


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--configs-path', default='data/configs.json')
    parser.add_argument('--pi')
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
    d4s7_mqtt = D4S7_Mqtt(configs)

    app.add_on_read_func(dht_mqtt.put)
    app.add_on_read_func(pir_mqtt.put)
    app.add_on_read_func(uds_mqtt.put)
    app.add_on_read_func(mds_mqtt.put)
    app.add_on_read_func(mbkp_mqtt.put)
    app.add_on_read_func(gyro_mqtt.put)
    app.add_on_event_func('buzzer', buzzer_mqtt.put)
    app.add_on_event_func('led', led_mqtt.put)
    app.add_on_event_func('lcd', lcd_mqtt.put)
    app.add_on_event_func('d4s7', d4s7_mqtt.put)


    # [7]
    app.add_on_read_func(read_GDHT_to_GLCD(app))
    # [1]
    app.add_on_read_func(on_DPIR_movement_turn_on_DL_for10s(app))
    # [2]
    app.add_on_read_func(on_DUS_add_userdata(app))
    app.add_on_read_func(on_DPIR_movement_detect_person_from_DUS(app))
    # [5]
    app.add_on_read_func(on_PIR_when_no_people_alarm(app))
    # [6]
    # ---- vvvv DEBUG ONLY vvvv -------------------------------------
    #
    def debug_event_callback_gsg_shake(device_cfg, data, event):
        if device_cfg['type'] != 'gyro':
            return
        debug_shake()
    app.add_on_event_func('gyro', debug_event_callback_gsg_shake)
    #                 
    # ---- ^^^^ DEBUG ONLY ^^^^ -------------------------------------
    app.add_on_read_func(on_GSG_motion_add_userdata(app))
    app.add_on_read_func(on_GSG_motion_check_for_alarm(app))


    websocket_if_alarm_then_turn_on_buzzer_else_turn_off_buzzer(app)



    app.run()

if __name__ == '__main__':
    main()
