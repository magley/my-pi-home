from app import App
import typing
import threading
from common import SensorConfig
import time
from components import dht
from components import pir
from components import buzzer
from components import mds
from components import led
from components import uds
from components import mbkp
from sensors.dht import DHTReading
from sensors.uds import UDSReading, UDSCode
from common import MyPiEventType
import RPi.GPIO as GPIO


def setup_devices(app: App):
    def make_thread(target: typing.Callable, *args):
        return threading.Thread(target=target, args=args, daemon=True)

    def pir_on_motion(config: SensorConfig):
        with app.print_lock:
            print(f"{time.strftime('%H:%M:%S', time.localtime())} {config.name} motion")

    def mds_on_read(config: SensorConfig, val: int):
        with app.print_lock:
            print(f"{time.strftime('%H:%M:%S', time.localtime())} {config.name} {val}")
    
    def dht_on_read(config: SensorConfig, reading: DHTReading):
        t = time.localtime()
        with app.print_lock:
            print(f"{time.strftime('%H:%M:%S', t)} {config.name} {reading.humidity}% {reading.temperature}°C")

    def uds_on_read(config: SensorConfig, reading: UDSReading):
        t = time.localtime()
        with app.print_lock:
            val = 'Timed out' if reading.code == UDSCode.TIMED_OUT else f"{reading.distance_in_cm}cm"
            print(f"{time.strftime('%H:%M:%S', t)} {config.name} {val}")

    def mbkp_on_read(config: SensorConfig, val: str):
        t = time.localtime()
        if val == '':
            return
        with app.print_lock:
            print(f"{time.strftime('%H:%M:%S', t)} {config.name} Input: {val}")

    GPIO.setmode(GPIO.BCM)
    for cfg in app.configs.values():
        match cfg.type:
            case 'dht':
                make_thread(dht.run, cfg, dht_on_read).start()
            case 'pir':
                pir.setup(cfg, pir_on_motion)
            case 'buzzer':
                buzzer.setup(cfg)
            case 'mds':
                make_thread(mds.run, cfg, mds_on_read)
            case 'led':
                led.setup(cfg)
            case 'uds':
                make_thread(uds.run, cfg, uds_on_read).start()
            case 'mbkp':
                make_thread(mbkp.run, cfg, mbkp_on_read).start()
            case _:
                raise Exception('Unknown config type')


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
                    buzzer.buzz(cfg)
                    with app.print_lock:
                        print(f"{time.strftime('%H:%M:%S', time.localtime())} {cfg.name} Start buzzing")
                case MyPiEventType.STOP_BUZZ:
                    cfg = app.event.sensor
                    buzzer.stop_buzz(cfg)
                    with app.print_lock:
                        print(f"{time.strftime('%H:%M:%S', time.localtime())} {cfg.name} Stop buzzing")
                case MyPiEventType.LED_ON:
                    cfg = app.event.sensor
                    led.turn_on(cfg)
                    with app.print_lock:
                        print(f"{time.strftime('%H:%M:%S', time.localtime())} {cfg.name} Turn on LED")
                case MyPiEventType.LED_OFF:
                    cfg = app.event.sensor
                    led.turn_off(cfg)
                    with app.print_lock:
                        print(f"{time.strftime('%H:%M:%S', time.localtime())} {cfg.name} Turn off LED")
                case _:
                    raise Exception('Unknown event type')
            app.event.consume()
