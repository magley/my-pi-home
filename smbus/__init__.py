class SMBus:
    def __init__(self, i: int):
        pass

    def write_byte(self, address: int, value: int):
        pass

    def write_byte_data(self, id: int, a_reg_add, bytes_val):
        pass

    def read_byte_data(self, id: int, a_reg_add) -> int:
        return 0x00000000