import logging

from .utils import *
from . import ev2300

from array import array

class BQ40Z50:
    def __init__(self):
        self.ev = ev2300.EV2300()
        self.ev.prepare()
        self.logger = logging.getLogger()

    def get_summary(self):
        serial_number = self.get_serial_number()
        print(f"serial_number: {serial_number}")
        soh = self.get_soh()
        print(f"soh: {soh}")

    def get_serial_number(self):
        serial_number_block = self.read_block(DEVICENAME_REG)
        if serial_number_block:
            serial_number = serial_number_block.tobytes().decode('utf-8').split(';')[0]
            return serial_number
        return None

    def get_soh(self):
        soh_word = self.read_word(SOH_REG)
        if soh_word:
            return ord(soh_word.decode('utf-8')[0])
        return None

    def read_block_mac(self, CMD: array) -> array:
        self.ev.smbus_write_block(DEV_ADDR, MAC_REG, CMD)
        block = self.ev.smbus_read_block(DEV_ADDR, MAC_REG)

        # First two block words need to be the command
        if len(CMD) > 1 and not block[0] == CMD[0] and not block[1] == CMD[1]:
            self.logger.warning("Read block CMD not correct")
            return None
        else:
            # Remove the cmd from the output block
            block.pop(0)
            block.pop(0)

        # Return as array object
        return block

    def read_block(self, CODE: array) -> array:
        return self.ev.smbus_read_block(DEV_ADDR, CODE)

    def read_word(self, REG: int):
        word = self.ev.smbus_read_word(DEV_ADDR, REG)
        if word:
            return word.to_bytes(16, byteorder='little')
        return None


    def bytes_to_str(self, input_b: bytes) -> str:
        output_str = ''
        l = len(input_b)
        # Convert from little endian
        for i in range(len(input_b)):
            output_str += '{0:b}'.format(input_b[l-i-1])
        return output_str

