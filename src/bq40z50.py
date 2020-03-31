import logging

from .utils import *
from . import ev2300

from array import array

class BQ40Z50:
    def __init__(self):
        self.ev = ev2300.EV2300()
        self.ev.prepare()
        self.logger = logging.getLogger()

    def read_block(self, CMD: array) -> bytes:
        self.ev.smbus_write_block(DEV_ADDR, MAC_REG, CMD)
        block = self.ev.smbus_read_block(DEV_ADDR, MAC_REG)

        # First two block words need to be the command
        if not block[0] == CMD[0] and not block[1] == CMD[1]:
            self.logger.warning("Read block CMD not correct")
            return None
        else:
            # Remove the cmd from the output block
            block.pop(0)
            block.pop(0)

        # Return as bytes object
        return block.tobytes()

    def bytes_to_str(self, input_b: bytes) -> str:
        output_str = ''
        l = len(input_b)
        # Convert from little endian
        for i in range(len(input_b)):
            output_str += '{0:b}'.format(input_b[l-i-1])
        return output_str

