import RPi.GPIO as GPIO
import typing
import time
import enum
import random


DHTLIB_DHT11_WAKEUP = 0.020
DHTLIB_TIMEOUT = 0.0001


class DHTCode(enum.Enum):
    DHTLIB_OK = enum.auto()
    DHTLIB_ERROR_CHECKSUM = enum.auto()
    DHTLIB_ERROR_TIMEOUT = enum.auto()


class DHTReading(typing.NamedTuple):
    humidity: int
    temperature: float
    code: DHTCode


def read_dht(pin: int, wakeup_delay = DHTLIB_DHT11_WAKEUP, timeout = DHTLIB_TIMEOUT):
        mask = 0x80
        idx = 0
        bits = [0,0,0,0,0]
        GPIO.setup(pin,GPIO.OUT)
        GPIO.output(pin,GPIO.LOW)
        time.sleep(wakeup_delay)
        GPIO.output(pin,GPIO.HIGH)
        #time.sleep(40*0.000001)
        GPIO.setup(pin,GPIO.IN)

        t = time.time()
        while(GPIO.input(pin) == GPIO.LOW):
            if((time.time() - t) > timeout):
                #print ("Echo LOW")
                return DHTReading(0, 0, DHTCode.DHTLIB_ERROR_TIMEOUT)
        t = time.time()
        while(GPIO.input(pin) == GPIO.HIGH):
            if((time.time() - t) > timeout):
                #print ("Echo HIGH")
                return DHTReading(0, 0, DHTCode.DHTLIB_ERROR_TIMEOUT)
        for i in range(0,40,1):
            t = time.time()
            while(GPIO.input(pin) == GPIO.LOW):
                if((time.time() - t) > timeout):
                    #print ("Data Low %d"%(i))
                    return DHTReading(0, 0, DHTCode.DHTLIB_ERROR_TIMEOUT)
            t = time.time()
            while(GPIO.input(pin) == GPIO.HIGH):
                if((time.time() - t) > timeout):
                    #print ("Data HIGH %d"%(i))
                    return DHTReading(0, 0, DHTCode.DHTLIB_ERROR_TIMEOUT)		
            if((time.time() - t) > 0.00005):	
                bits[idx] |= mask
            #print("t : %f"%(time.time()-t))
            mask >>= 1
            if(mask == 0):
                mask = 0x80
                idx += 1	
        #print (.bits)
        GPIO.setup(pin,GPIO.OUT)
        GPIO.output(pin,GPIO.HIGH)
        sum_chk = ((bits[0] + bits[1] + bits[2] + bits[3]) & 0xFF)
        if(bits[4] is not sum_chk):
            return DHTReading(0, 0, DHTCode.DHTLIB_ERROR_CHECKSUM)
        humidity = bits[0]
        temperature = bits[2] + bits[3] * 0.1
        return DHTReading(humidity, temperature, DHTCode.DHTLIB_OK)


# FIXME: This simulator is very primitive. Do something that will produce a wider (yet believable) range of results
def read_dht_simulated():
    temperature = 25 + random.randint(-1, 1)
    humidity = 25 +  random.randint(-1, 1)
    return DHTReading(temperature, humidity, DHTCode.DHTLIB_OK)
