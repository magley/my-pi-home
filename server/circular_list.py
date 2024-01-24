class CircularList:
    """
    Appends data in a circle, looping around at the last value to the first.
    """
    def __init__(self, maxlen: int):
        self._maxlen = maxlen
        self._data = [''] * maxlen
        self.cur_idx = 0

    def append(self, val):
        self._data[self.cur_idx] = val
        self.cur_idx = (self.cur_idx + 1) % self._maxlen


    def circular_equal(self, other):
        """
        Matches other so that the last _maxlen elements starting from cur_idx are equal.
        For example, 3412 will match other=1234
                       ^cur_idx
        """
        if len(self._data) != len(other):
            return False
        idx = self.cur_idx
        for val in reversed(other):
            idx = (idx - 1) % self._maxlen
            if val != self._data[idx]:
                return False
        return True


    def as_str(self):
        return ''.join(self._data)
