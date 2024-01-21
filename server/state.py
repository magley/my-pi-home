class State(object):
    def __init__(self):
        self._number_of_people = 0
        self._alarm = False
        self._wakeup = ""
        self._is_wakeup_active = False

        # Each key is device code ('RDHT1', 'DS1', ...)
        # Value is a python dict containing all relevant data.
        self.device_state = {}

    def person_enter(self):
        self._number_of_people += 1

    def person_exit(self):
        self._number_of_people -= 1

        # In practice, this if never enters. Not the case for simulators.
        if self._number_of_people < 0:
            self._number_of_people = 0

    def set_alarm(self, is_alarm_active: bool):
        self._alarm = is_alarm_active

    def set_wakeup(self, wakeup: str):
        self._wakeup = wakeup

    def set_is_wakeup_active(self, is_wakeup_active: bool):
        self._is_wakeup_active = is_wakeup_active

    def update_device_state(self, single_device_state_dict: dict):
        """
            Called on each device reading.
            If a device has multiple fields, that's multiple calls of this function as per MQTT.
            In that case, we UPDATE the values for those keys, while keeping the old ones.
            So, in a way, this function partially updates the state for some device.

            ```
            {
                "name": "RDHT1",
                "runs_on": "PI1",
                "measurement": "temperature",
                "value": 29,
                "timestamp_": 1712247928.12732
            }
            ```
            This would translate into:
            ```
            self.device_state = {
                "RDHT1": {
                    "runs_on": "PI1",
                    "temperature": 29,
                }
            }
            ```
            If the next measurement was with humidity instead of temperature for RDHT1, then:
            ```
            self.device_state = {
                "RDHT1": {
                    "runs_on": "PI1",
                    "temperature": 29,
                    "humidity": 43,
                }
            }
            ```  
        """
        key = single_device_state_dict['name']
        val = self.device_state.get(key, {})

        is_newer = True
        if "timestamp_" in val:
            if val["timestamp_"] > single_device_state_dict["timestamp_"]:
                is_newer = False
        
        if not is_newer:
            return

        for k, v in single_device_state_dict.items():
            if k not in ['measurement', 'value']:
                val[k] = v
        val[single_device_state_dict['measurement']] = single_device_state_dict['value']
        self.device_state[key] = val
       

    @property
    def number_of_people(self):
        return self._number_of_people
    
    @property
    def alarm(self):
        return self._alarm
    
    @property
    def wakeup(self):
        return self._wakeup

    @property
    def is_wakeup_active(self):
        return self._is_wakeup_active
