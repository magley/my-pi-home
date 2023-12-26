class State:
    def __init__(self):
        self._number_of_people = 0

    def person_enter(self):
        self._number_of_people += 1

    def person_exit(self):
        self._number_of_people -= 1

    @property
    def number_of_people(self):
        return self._number_of_people