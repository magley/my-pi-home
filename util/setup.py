from util.app import App
import threading
from util.common import SensorConfig
import time
import util.devices as devs
from sensors.dht import DHTReading
from sensors.uds import UDSReading, UDSCode
from util.common import MyPiEventType
import RPi.GPIO as GPIO


def setup_devices(app: App):
    def make_reader(*args):
        return threading.Thread(target=devs.run_reader, args=args, daemon=True).start()

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
                    with app.print_lock:
                        print(f"~~~ {time.strftime('%H:%M:%S', time.localtime())} {cfg.name} Start buzzing")
                case MyPiEventType.STOP_BUZZ:
                    cfg = app.event.sensor
                    devs.buzzer_stop_buzz(cfg)
                    with app.print_lock:
                        print(f"~~~ {time.strftime('%H:%M:%S', time.localtime())} {cfg.name} Stop buzzing")
                case MyPiEventType.LED_ON:
                    cfg = app.event.sensor
                    devs.led_turn_on(cfg)
                    with app.print_lock:
                        print(f"~~~ {time.strftime('%H:%M:%S', time.localtime())} {cfg.name} Turn on LED")
                case MyPiEventType.LED_OFF:
                    cfg = app.event.sensor
                    devs.led_turn_off(cfg)
                    with app.print_lock:
                        print(f"~~~ {time.strftime('%H:%M:%S', time.localtime())} {cfg.name} Turn off LED")
                case _:
                    raise Exception('Unknown event type')
            app.event.consume()
