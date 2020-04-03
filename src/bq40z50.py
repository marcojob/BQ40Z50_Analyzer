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

        lifetime_1_dict = self.get_lifetime_1()
        print(lifetime_1_dict)

        lifetime_2_dict = self.get_lifetime_2()
        print(lifetime_2_dict)

        lifetime_3_dict = self.get_lifetime_3()
        print(lifetime_3_dict)

        lifetime_4_dict = self.get_lifetime_4()
        print(lifetime_4_dict)

        lifetime_5_dict = self.get_lifetime_5()
        print(lifetime_5_dict)

    def get_lifetime_5(self):
        lifetime_block = self.read_block_mac(LIFETIMEDATABLOCK5_CMD)
        lifetime = dict()

        if lifetime_block:
            # Shortcircuit during charge
            lifetime['N ASCC ev'] = (lifetime_block[1] << 8) | lifetime_block[0]
            lifetime['Last ASCC ev'] = (lifetime_block[3] << 8) | lifetime_block[2]

            # Overtemperature during charge
            lifetime['N OTC ev'] = (lifetime_block[5] << 8) | lifetime_block[4]
            lifetime['Last OTC ev'] = (lifetime_block[7] << 8) | lifetime_block[6]

            # Overtemperature during discharge
            lifetime['N OTD ev'] = (lifetime_block[9] << 8) | lifetime_block[8]
            lifetime['Last OTD ev'] = (lifetime_block[11] << 8) | lifetime_block[10]

            # Overtemperature FET
            lifetime['N OTF ev'] = (lifetime_block[13] << 8) | lifetime_block[12]
            lifetime['Last OTF ev'] = (lifetime_block[15] << 8) | lifetime_block[14]

            # Total number of valid charge terminations
            lifetime['N valid charge term'] = (lifetime_block[17] << 8) | lifetime_block[16]
            lifetime['Last valid charge term'] = (lifetime_block[19] << 8) | lifetime_block[18]

            # Total number of QMax updates
            lifetime['N Qmax update'] = (lifetime_block[21] << 8) | lifetime_block[20]
            lifetime['Last Qmax update'] = (lifetime_block[23] << 8) | lifetime_block[22]

            # Total number of resistance updates
            lifetime['N Ra updates'] = (lifetime_block[25] << 8) | lifetime_block[24]
            lifetime['Last Ra update'] = (lifetime_block[27] << 8) | lifetime_block[26]

            # Total number of resistances updates
            lifetime['N Ra disable'] = (lifetime_block[29] << 8) | lifetime_block[28]
            lifetime['Last Ra disable'] = (lifetime_block[31] << 8) | lifetime_block[30]

        return lifetime

    def get_lifetime_4(self):
        lifetime_block = self.read_block_mac(LIFETIMEDATABLOCK4_CMD)
        lifetime = dict()

        if lifetime_block:
            # Cell Overvoltage Events
            lifetime['N COV ev'] = (lifetime_block[1] << 8) | lifetime_block[0]
            lifetime['Last COV ev'] = (lifetime_block[3] << 8) | lifetime_block[2]

            # Cell Undervoltage Events
            lifetime['N CUV ev'] = (lifetime_block[5] << 8) | lifetime_block[4]
            lifetime['Last CUV ev'] = (lifetime_block[7] << 8) | lifetime_block[6]

            # Over Current Discharge Tier 1
            lifetime['N OCD1 ev'] = (lifetime_block[9] << 8) | lifetime_block[8]
            lifetime['Last OCD1 ev'] = (lifetime_block[11] << 8) | lifetime_block[10]

            # Over Current Discharge Tier 2
            lifetime['N OCD2 ev'] = (lifetime_block[13] << 8) | lifetime_block[12]
            lifetime['Last OCD2 ev'] = (lifetime_block[15] << 8) | lifetime_block[14]

            # Over Current Charge Tier 1
            lifetime['N OCC1 ev'] = (lifetime_block[17] << 8) | lifetime_block[16]
            lifetime['Last OCC1 ev'] = (lifetime_block[19] << 8) | lifetime_block[18]

            # Over Current Charge Tier 2
            lifetime['N OCC2 ev'] = (lifetime_block[21] << 8) | lifetime_block[20]
            lifetime['Last OCC2 ev'] = (lifetime_block[23] << 8) | lifetime_block[22]

            # Overload in Discharge Protection
            lifetime['N AOLD ev'] = (lifetime_block[25] << 8) | lifetime_block[24]
            lifetime['Last AOLD ev'] = (lifetime_block[27] << 8) | lifetime_block[26]

            # Short circuit in Discharge
            lifetime['N ASCD ev'] = (lifetime_block[29] << 8) | lifetime_block[28]
            lifetime['Last ASCD ev'] = (lifetime_block[31] << 8) | lifetime_block[30]

        return lifetime

    def get_lifetime_3(self):
        lifetime_block = self.read_block_mac(LIFETIMEDATABLOCK3_CMD)
        lifetime = dict()

        if lifetime_block:
            # Total firmware runtime [2h]
            lifetime['Total FW Runtime'] = (lifetime_block[1] << 8) | lifetime_block[0]

            # Total firmware runtime spent below T1 [2h]
            lifetime['Time UT'] = (lifetime_block[3] << 8) | lifetime_block[2]

            # Total firmware runtime spent between T1 and T2 [2h]
            lifetime['Time LT'] = (lifetime_block[5] << 8) | lifetime_block[4]

            # Total firmware runtime spent between T2 and T5 [2h]
            lifetime['Time STL'] = (lifetime_block[7] << 8) | lifetime_block[6]

            # Total firmware runtime spent between T5 and T6 [2h]
            lifetime['Time RT'] = (lifetime_block[9] << 8) | lifetime_block[8]

            # Total firmware runtime spent between T6 and T3 [2h]
            lifetime['Time STH'] = (lifetime_block[11] << 8) | lifetime_block[10]

            # Total firmware runtime spent between T3 and T4 [2h]
            lifetime['Time HT'] = (lifetime_block[13] << 8) | lifetime_block[12]

            # Total firmware runtime spent above T6 [2h]
            lifetime['Time OT'] = (lifetime_block[15] << 8) | lifetime_block[14]

        return lifetime

    def get_lifetime_2(self) -> dict:
        lifetime_block = self.read_block_mac(LIFETIMEDATABLOCK2_CMD)
        lifetime = dict()

        if lifetime_block:
            lifetime['N shutdowns'] = lifetime_block[0]
            lifetime['N partial resets'] = lifetime_block[1]
            lifetime['N full resets'] = lifetime_block[2]
            lifetime['N WDT resets'] = lifetime_block[3]

            # CB = Cell Balancing
            lifetime['CB Time Cell 1 [2h]'] = lifetime_block[4]
            lifetime['CB Time Cell 2 [2h]'] = lifetime_block[5]
            lifetime['CB Time Cell 3 [2h]'] = lifetime_block[6]
            lifetime['CB Time Cell 4 [2h]'] = lifetime_block[7]

        return lifetime

    def get_lifetime_1(self) -> dict:
        lifetime_block = self.read_block_mac(LIFETIMEDATABLOCK1_CMD)
        lifetime = dict()

        if lifetime_block:
            # Max voltages
            lifetime['Cell 1 max mV'] = (lifetime_block[1] << 8) | lifetime_block[0]
            lifetime['Cell 2 max mV'] = (lifetime_block[3] << 8) | lifetime_block[2]
            lifetime['Cell 3 max mV'] = (lifetime_block[5] << 8) | lifetime_block[4]
            lifetime['Cell 4 max mV'] = (lifetime_block[7] << 8) | lifetime_block[6]

            # Min voltages
            lifetime['Cell 1 min mV'] = (lifetime_block[9] << 8) | lifetime_block[8]
            lifetime['Cell 2 min mV'] = (lifetime_block[11] << 8) | lifetime_block[10]
            lifetime['Cell 3 min mV'] = (lifetime_block[13] << 8) | lifetime_block[12]
            lifetime['Cell 4 min mV'] = (lifetime_block[15] << 8) | lifetime_block[14]

            # Max delta cell voltages
            lifetime['Max Delta Cell mV'] = (lifetime_block[17] << 8) | lifetime_block[16]

            # Max charge current
            lifetime['Max Charge mA'] = (lifetime_block[19] << 8) | lifetime_block[18]

            # Max discharge current
            lifetime['Max Discharge mA'] = (lifetime_block[21] << 8) | lifetime_block[20]

            # Max Avg Dsg Current
            lifetime['Max Avg Dsg mA'] = (lifetime_block[23] << 8) | lifetime_block[22]

            # Max Avg Dsg Power
            lifetime['Max Avg Dsg mW'] = (lifetime_block[25] << 8) | lifetime_block[24]

            # Max Temp Cell
            lifetime['Max temp cell'] = lifetime_block[26]

            # Min Temp Cell
            lifetime['Min temp cell'] = lifetime_block[27]

            # Max Delta Cell temp
            lifetime['Max delta cell temp'] = lifetime_block[28]

            # Max Temp Int Sensor
            lifetime['Max Temp Int Sensor'] = lifetime_block[29]

            # Min Temp Int Sensor
            lifetime['Min Temp Int Sensor'] = lifetime_block[30]

            #Max Temp Fet
            lifetime['Max Temp Fet'] = lifetime_block[31]

        return lifetime

    def get_serial_number(self) -> str:
        serial_number_block = self.read_block(DEVICENAME_REG)
        if serial_number_block:
            serial_number = serial_number_block.tobytes().decode('utf-8').split(';')[0]
            return serial_number
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

    def bytes_to_str(self, input_b: bytes, l) -> str:
        output_str = ''
        for i in range(l):
            output_str += '{:08b}'.format(input_b[i])
        return output_str

