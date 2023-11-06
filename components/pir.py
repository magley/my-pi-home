import sensors.pir as pir
import functools
import time
import typing
import config
import threading


def run(config: config.SensorConfig, stop_event: threading.Event, lock: threading.Lock):
    reader = _get_reader(config)
    while True:
        if stop_event.is_set():
            print('Stopping pir loop')
            break
        reading = reader()
        _print_reading(reading, config, lock)
        time.sleep(config.read_interval)


def _print_reading(reading: pir.PIRReading, config: config.SensorConfig, lock: threading.Lock):
    t = time.localtime()

    with lock:
        print("-" * 25)
        print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
        print(f"Sensor: {config.name}")
        print(f"Motion: {'YES' if reading.motion else 'NO'}")



def _get_reader(config: config.SensorConfig):
    if not config.simulated:
        return functools.partial(pir.read, pin=config.pin)
    else:
        return pir.Simulator().read