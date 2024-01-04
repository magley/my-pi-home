class State:
    def __init__(self):
        self._number_of_people = 0
        self._alarm = False

    def person_enter(self):
        self._number_of_people += 1

    def person_exit(self):
        self._number_of_people -= 1

        # In practice, this if never enters. Not the case for simulators.
        if self._number_of_people < 0:
            self._number_of_people = 0

    def set_alarm(self, is_alarm_active: bool):
        self._alarm = is_alarm_active

    @property
    def number_of_people(self):
        return self._number_of_people
    
    @property
    def alarm(self):
        return self._alarm