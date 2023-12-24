import random
from common.mqtt import MqttSender, build_payload
from components.gyro_util import MPU6050

# Only one gyroscope in the project so global variable is Ok.
_mpu = MPU6050.MPU6050()


class Gyro_Mqtt(MqttSender):
    def __init__(self, config: dict):
        super().__init__(config)
        self.topic = "iot/gyro"


    def put(self, cfg: dict, data: dict):
        if cfg['type'] != 'gyro':
            return

        self.do_put(build_payload(cfg, data, "accel.x"))
        self.do_put(build_payload(cfg, data, "accel.y"))
        self.do_put(build_payload(cfg, data, "accel.z"))
        self.do_put(build_payload(cfg, data, "gyro.x"))
        self.do_put(build_payload(cfg, data, "gyro.y"))
        self.do_put(build_payload(cfg, data, "gyro.z"))


def get_reader_func(cfg: dict):
    if cfg['simulated']:
        return read_sim
    return read_real


def _reading(accel: list[float], gyro: list[float]):
    # Force it to be float. Otherwise influx db WILL complain if you mix int and float.
    for a in accel:
        a = float(a)
    for g in gyro:
        g = float(g)

    return { 
        "accel.x": accel[0],
        "accel.y": accel[1],
        "accel.z": accel[2],
        "gyro.x": gyro[0],
        "gyro.y": gyro[1],
        "gyro.z": gyro[2],
    }


def setup():
    _mpu.dmp_initialize()


def read_sim():
    accel = [random.random(), random.random(), 9.81 + random.random()]
    gyro = [random.random() * 5.0, random.random() * 5.0, random.random() * 5.0]
    return _reading(accel, gyro)


def read_real(): 
    accel = _mpu.get_acceleration()
    gyro = _mpu.get_rotation()
    return _reading(accel, gyro)