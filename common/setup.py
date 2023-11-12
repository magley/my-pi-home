from common.app import App
import threading
from common.config import SensorConfig
import time
import common.devices as devs
from sensors.dht import DHTReading
from sensors.uds import UDSReading, UDSCode
from common.event import MyPiEventType
import RPi.GPIO as GPIO
import common.colorizer as colorizer
import random as rnd


def setup_devices(app: App):
    def put(item: str, color: str):
        app.print_thread.put(item, color)

    def make_reader(*args):
        return threading.Thread(target=devs.run_reader, args=args, daemon=True).start()

    def pir_on_motion(config: SensorConfig):
        t = time.localtime()
        put((f"{time.strftime('%H:%M:%S', t)} {config.name} motion"), app.configs_colors[config.name])

    def mds_on_read(config: SensorConfig, val: int):
        t = time.localtime()
        put(f"{time.strftime('%H:%M:%S', t)} {config.name} {val}", app.configs_colors[config.name])
    
    def dht_on_read(config: SensorConfig, reading: DHTReading):
        t = time.localtime()
        put(f"{time.strftime('%H:%M:%S', t)} {config.name} {reading.humidity}% {reading.temperature}°C", app.configs_colors[config.name])

    def uds_on_read(config: SensorConfig, reading: UDSReading):
        t = time.localtime()
        val = 'Timed out' if reading.code == UDSCode.TIMED_OUT else f"{reading.distance_in_cm}cm"
        put(f"{time.strftime('%H:%M:%S', t)} {config.name} {val}", app.configs_colors[config.name])

    def mbkp_on_read(config: SensorConfig, val: str):
        t = time.localtime()
        if val == '':
            return
        put(f"{time.strftime('%H:%M:%S', t)} {config.name} Input: {val}", app.configs_colors[config.name])


    available_colors = colorizer.available_colors()
    app.configs_colors = {name: 'WHITE' for name in app.configs.keys()}


    GPIO.setmode(GPIO.BCM)
    for cfg in app.configs.values():
        if len(available_colors) != 0:
            app.configs_colors[cfg.name] = available_colors.pop(rnd.randint(0, len(available_colors) - 1))
        match cfg.type:
            case 'dht':
                # dht doesn't have a setup because its reader alternates
                # dht's pin between IN and OUT
                make_reader(cfg, devs.dht_get_reader, dht_on_read)
            case 'pir':
                devs.pir_setup(cfg, pir_on_motion)
            case 'buzzer':
                devs.buzzer_setup(cfg)
            case 'mds':
                devs.mds_setup(cfg)
                make_reader(cfg, devs.mds_get_reader, mds_on_read)
            case 'led':
                devs.led_setup(cfg)
            case 'uds':
                devs.uds_setup(cfg)
                make_reader(cfg, devs.uds_get_reader, uds_on_read)
            case 'mbkp':
                devs.mbkp_setup(cfg)
                make_reader(cfg, devs.mbkp_get_reader, mbkp_on_read)
            case _:
                raise Exception('Unknown config type')


def cleanup_devices():
    GPIO.cleanup()


def start_event_thread(app: App):
    threading.Thread(target=_event_thread, args=(app,), daemon=True).start()


def _event_thread(app: App):
    while True:
        if app.event.wait():
            match app.event.type:
                case MyPiEventType.EMPTY:
                    raise Exception('We should not see the EMPTY event.')
                case MyPiEventType.BUZZ:
                    cfg = app.event.sensor
                    devs.buzzer_buzz(cfg)
                    app.print_thread.put(f"~~~ {time.strftime('%H:%M:%S', time.localtime())} {cfg.name} Start buzzing", app.configs_colors[cfg.name], True)
                case MyPiEventType.STOP_BUZZ:
                    cfg = app.event.sensor
                    devs.buzzer_stop_buzz(cfg)
                    app.print_thread.put(f"~~~ {time.strftime('%H:%M:%S', time.localtime())} {cfg.name} Stop buzzing", app.configs_colors[cfg.name], True)
                case MyPiEventType.LED_ON:
                    cfg = app.event.sensor
                    devs.led_turn_on(cfg)
                    app.print_thread.put(f"~~~ {time.strftime('%H:%M:%S', time.localtime())} {cfg.name} Turn on LED", app.configs_colors[cfg.name], True)
                case MyPiEventType.LED_OFF:
                    cfg = app.event.sensor
                    devs.led_turn_off(cfg)
                    app.print_thread.put(f"~~~ {time.strftime('%H:%M:%S', time.localtime())} {cfg.name} Turn off LED", app.configs_colors[cfg.name], True)
                case _:
                    raise Exception('Unknown event type')
            app.event.consume()
