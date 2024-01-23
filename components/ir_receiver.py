import RPi.GPIO as GPIO
import random
import time
from datetime import datetime


from common.mqtt import MqttSender, build_payload


class IR_Receiver_Mqtt(MqttSender):
    def __init__(self, config: dict):
        super().__init__(config)
        self.topic = "iot/ir_receiver"


    def put(self, cfg: dict, data: dict):
        if cfg['type'] != 'ir_receiver':
            return
        
        payload = build_payload(cfg, data, "btn")
        self.do_put(payload)


def setup(pin: int, is_simulated: bool):
    if is_simulated:
        return
    GPIO.setup(pin, GPIO.IN)


def get_reader_func(cfg: dict):
    if cfg['simulated']:
        return read_sim
    return lambda: read_real(cfg['pins'][0])


def _reading(btn: str):
    return { "btn": btn }


Buttons = [0x300ff22dd, 0x300ffc23d, 0x300ff629d, 0x300ffa857, 0x300ff9867, 0x300ffb04f, 0x300ff6897, 0x300ff02fd, 0x300ff30cf, 0x300ff18e7, 0x300ff7a85, 0x300ff10ef, 0x300ff38c7, 0x300ff5aa5, 0x300ff42bd, 0x300ff4ab5, 0x300ff52ad]  # HEX code list
ButtonsNames = ["LEFT",   "RIGHT",      "UP",       "DOWN",       "2",          "3",          "1",        "OK",        "4",         "5",         "6",         "7",         "8",          "9",        "*",         "0",        "#"]  # String list in same order as HEX list


def read_sim():
    return _reading(ButtonsNames[random.randint(0, len(ButtonsNames) - 1)])


def getBinary(pin: int):
	# Internal vars
	num1s = 0  # Number of consecutive 1s read
	binary = 1  # The binary value
	command = []  # The list to store pulse times in
	previousValue = 0  # The last value
	value = GPIO.input(pin)  # The current value

	# Waits for the sensor to pull pin low
	while value:
		time.sleep(0.0001) # This sleep decreases CPU utilization immensely
		value = GPIO.input(pin)
		
	# Records start time
	startTime = datetime.now()
	
	while True:
		# If change detected in value
		if previousValue != value:
			now = datetime.now()
			pulseTime = now - startTime #Calculate the time of pulse
			startTime = now #Reset start time
			command.append((previousValue, pulseTime.microseconds)) #Store recorded data
			
		# Updates consecutive 1s variable
		if value:
			num1s += 1
		else:
			num1s = 0
		
		# Breaks program when the amount of 1s surpasses 10000
		if num1s > 10000:
			break
			
		# Re-reads pin
		previousValue = value
		value = GPIO.input(pin)
		
	# Converts times to binary
	for (typ, tme) in command:
		if typ == 1: #If looking at rest period
			if tme > 1000: #If pulse greater than 1000us
				binary = binary *10 +1 #Must be 1
			else:
				binary *= 10 #Must be 0
			
	if len(str(binary)) > 34: #Sometimes, there is some stray characters
		binary = int(str(binary)[:34])
		
	return binary
	
# Convert value to hex
def convertHex(binaryValue):
	tmpB2 = int(str(binaryValue),2) #Temporarely propper base 2
	return hex(tmpB2)


def read_real(pin: int):
	inData = convertHex(getBinary(pin)) #Runs subs to get incoming hex value
	for button in range(len(Buttons)):#Runs through every value in list
		if hex(Buttons[button]) == inData: #Checks this against incoming
			return _reading(ButtonsNames[button]) #Prints corresponding english name for button
