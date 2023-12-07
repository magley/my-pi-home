from common.app import App
import threading
from common.config import DeviceConfig
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

    def pir_on_motion(config: DeviceConfig):
        t = time.localtime()
        put((f"{time.strftime('%H:%M:%S', t)} {config.name} motion"), app.configs_colors[config.name])

    def mds_on_read(config: DeviceConfig, val: int):
        t = time.localtime()
        put(f"{time.strftime('%H:%M:%S', t)} {config.name} {val}", app.configs_colors[config.name])
    
    def dht_on_read(config: DeviceConfig, reading: DHTReading):
        t = time.localtime()
        put(f"{time.strftime('%H:%M:%S', t)} {config.name} {reading.humidity}% {reading.temperature}°C", app.configs_colors[config.name])

    def uds_on_read(config: DeviceConfig, reading: UDSReading):
        t = time.localtime()
        val = 'Timed out' if reading.code == UDSCode.TIMED_OUT else f"{reading.distance_in_cm}cm"
        put(f"{time.strftime('%H:%M:%S', t)} {config.name} {val}", app.configs_colors[config.name])

    def mbkp_on_read(config: DeviceConfig, val: str):
        t = time.localtime()
        if val == '':
            return
        put(f"{time.strftime('%H:%M:%S', t)} {config.name} Input: {val}", app.configs_colors[config.name])


    available_colors = colorizer.available_colors()
    app.configs_colors = {name: 'WHITE' for name in app.config.devices.keys()}


    GPIO.setmode(GPIO.BCM)
    for cfg in app.config.devices.values():
        if len(available_colors) != 0:
            app.configs_colors[cfg.name] = available_colors.pop(rnd.randint(0, len(available_colors) - 1))
            if cfg.type == 'dht':
                # dht doesn't have a setup because its reader alternates
                # dht's pin between IN and OUT
                make_reader(cfg, devs.dht_get_reader, dht_on_read)
            elif cfg.type == 'pir':
                devs.pir_setup(cfg, pir_on_motion)
            elif cfg.type ==  'buzzer':
                devs.buzzer_setup(cfg)
            elif cfg.type ==  'mds':
                devs.mds_setup(cfg)
                make_reader(cfg, devs.mds_get_reader, mds_on_read)
            elif cfg.type ==  'led':
                devs.led_setup(cfg)
            elif cfg.type ==  'uds':
                devs.uds_setup(cfg)
                make_reader(cfg, devs.uds_get_reader, uds_on_read)
            elif cfg.type ==  'mbkp':
                devs.mbkp_setup(cfg)
                make_reader(cfg, devs.mbkp_get_reader, mbkp_on_read)
            else:
                raise Exception('Unknown config type')


def cleanup_devices():
    GPIO.cleanup()


def start_event_thread(app: App):
    threading.Thread(target=_event_thread, args=(app,), daemon=True).start()


def _event_thread(app: App):
    while True:
        if app.event.wait():
            if app.event.type ==  MyPiEventType.EMPTY:
                raise Exception('We should not see the EMPTY event.')
            elif app.event.type ==  MyPiEventType.BUZZ:
                cfg = app.event.cfg
                devs.buzzer_buzz(cfg)
                app.print_thread.put(f"~~~ {time.strftime('%H:%M:%S', time.localtime())} {cfg.name} Start buzzing", app.configs_colors[cfg.name], True)
            elif app.event.type ==  MyPiEventType.STOP_BUZZ:
                cfg = app.event.cfg
                devs.buzzer_stop_buzz(cfg)
                app.print_thread.put(f"~~~ {time.strftime('%H:%M:%S', time.localtime())} {cfg.name} Stop buzzing", app.configs_colors[cfg.name], True)
            elif app.event.type ==  MyPiEventType.LED_ON:
                cfg = app.event.cfg
                devs.led_turn_on(cfg)
                app.print_thread.put(f"~~~ {time.strftime('%H:%M:%S', time.localtime())} {cfg.name} Turn on LED", app.configs_colors[cfg.name], True)
            elif app.event.type ==  MyPiEventType.LED_OFF:
                cfg = app.event.cfg
                devs.led_turn_off(cfg)
                app.print_thread.put(f"~~~ {time.strftime('%H:%M:%S', time.localtime())} {cfg.name} Turn off LED", app.configs_colors[cfg.name], True)
            else:
                raise Exception('Unknown event type')
            app.event.consume()
