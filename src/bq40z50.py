import logging

from .utils import *
from . import ev2300

from array import array
from time import sleep

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

        safety_status_dict = self.get_safety_status()
        print(safety_status_dict)

        battery_status_dict = self.get_battery_status()
        print(battery_status_dict)

        operation_status = self.get_operation_status()
        print(operation_status)

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
            return word
        return None

    def bytes_to_str(self, input_b: bytes, l: int) -> str:
        output_str = ''
        for i in range(l):
            output_str += '{:08b}'.format(input_b[i])
        return output_str

    def get_bit(self, input_b: bytes, index: int) -> int:
        return (input_b >> index) & 1

    def try_unseal(self):
        self.unseal(0x79E6, 0x428A)
        sleep(0.1)
        print(self.is_sealed())
        sleep(0.1)

        self.unseal(0x428A, 0x79E6)
        sleep(0.1)
        print(self.is_sealed())
        sleep(0.1)

        self.unseal(0xC3B1, 0x50DF)
        sleep(0.1)
        print(self.is_sealed())
        sleep(0.1)

        self.unseal(0x50DF, 0xC3B1)
        sleep(0.1)
        print(self.is_sealed())
        sleep(0.1)

        block = self.read_block_mac(array('B', b'\x40\x00'))
        print(block)
        sleep(0.1)

    def is_sealed(self) -> bool:
        operation_status_block = self.read_block_mac(OPERATIONSTATUS_CMD)
        # sec = (self.get_bit(operation_status_block[2], 1) << 1) | self.get_bit(operation_status_block[2], 0)
        sec = (self.get_bit(operation_status_block[1], 0) << 1) | self.get_bit(operation_status_block[1], 1)
        print(sec)
        if sec == 1 or sec == 2:
            return False
        return True

    def unseal(self, word1, word2):
        self.ev.smbus_write_word(DEV_ADDR, 0x00, word1)
        self.ev.smbus_write_word(DEV_ADDR, 0x00, word2)

    def get_operation_status(self):
        operation_status_block = self.read_block_mac(OPERATIONSTATUS_CMD)
        operation_status = dict()

        if operation_status_block:
            # Emergency FET shutdown
            operation_status['EMSHUT'] = self.get_bit(operation_status_block[0], 5)

            # Cell balancing status
            operation_status['CB'] = self.get_bit(operation_status_block[0], 4)

            # CC measurements in SLEEP
            operation_status['SLPCC'] = self.get_bit(operation_status_block[0], 3)

            # ADC measurements in SLEEP
            operation_status['SLPAD'] = self.get_bit(operation_status_block[0], 2)

            # Auto CC calibration
            operation_status['SMBLCAL'] = self.get_bit(operation_status_block[0], 1)

            # Initialization after full reset
            operation_status['INIT'] = self.get_bit(operation_status_block[0], 0)

            # SLEEP mode triggered via command
            operation_status['SLEEPM'] = self.get_bit(operation_status_block[1], 7)

            # 400 kHz SMBUS mode
            operation_status['XL'] = self.get_bit(operation_status_block[1], 6)

            # Calibration Output
            operation_status['CAL_OFFSET'] = self.get_bit(operation_status_block[1], 5)

            # Calibration Output
            operation_status['CAL'] = self.get_bit(operation_status_block[1], 4)

            # Auto CC Offset Calibration
            operation_status['AUTOCALM'] = self.get_bit(operation_status_block[1], 3)

            # Authentication in progress
            operation_status['AUTH'] = self.get_bit(operation_status_block[1], 2)

            # LED display
            operation_status['LED'] = self.get_bit(operation_status_block[1], 1)

            # Shutdown triggered via command
            operation_status['SDM'] = self.get_bit(operation_status_block[1], 0)

            # SLEEP conditions met
            operation_status['SLEEP'] = self.get_bit(operation_status_block[2], 7)

            # Charging disabled
            operation_status['XCHG'] = self.get_bit(operation_status_block[2], 6)

            # Discharging disabled
            operation_status['XDSG'] = self.get_bit(operation_status_block[2], 5)

            # PERMANENT FAILURE mode status
            operation_status['PF'] = self.get_bit(operation_status_block[2], 4)

            # SAFETY status
            operation_status['SS'] = self.get_bit(operation_status_block[2], 3)

            # Shutdown triggered via low pack voltage
            operation_status['SDV'] = self.get_bit(operation_status_block[2], 2)

            sec = (self.get_bit(operation_status_block[2], 1) << 1) | self.get_bit(operation_status_block[2], 0)
            if sec == 0:
                operation_status['SEC'] = 'Reserved'
            elif sec == 1:
                operation_status['SEC'] = 'Full Access'
            elif sec == 2:
                operation_status['SEC'] = 'Unsealed'
            elif sec == 3:
                operation_status['SEC'] = 'Sealed'

            # Battery Trip Point Interrupt
            operation_status['BTP_INT'] = self.get_bit(operation_status_block[3], 7)

            # Fuse status
            operation_status['FUSE'] = self.get_bit(operation_status_block[3], 5)

            # Precharge FET Status
            operation_status['PCHG'] = self.get_bit(operation_status_block[3], 3)

            # CHG FET status
            operation_status['CHG'] = self.get_bit(operation_status_block[3], 2)

            # DSG FET status
            operation_status['DSG'] = self.get_bit(operation_status_block[3], 1)

            # Syste present low
            operation_status['PRES'] = self.get_bit(operation_status_block[3], 0)

        return operation_status

    def get_battery_status(self):
        battery_status_word = self.read_word(BATTERYSTATUS_REG)
        battery_status = dict()

        if battery_status_word:
            # Overcharged alarm
            battery_status['OCA'] = self.get_bit(battery_status_word, 15)

            # Terminate charge alarm
            battery_status['TCA'] = self.get_bit(battery_status_word, 14)

            # Overtemperature alarm
            battery_status['OTA'] = self.get_bit(battery_status_word, 12)

            # Terimnate discharge alarm
            battery_status['TDA'] = self.get_bit(battery_status_word, 11)

            # Remaining capacity alarm
            battery_status['RCA'] = self.get_bit(battery_status_word, 9)

            # Remaining time alarm
            battery_status['RTA'] = self.get_bit(battery_status_word, 8)

            # Gauge initialization completed
            battery_status['INIT'] = self.get_bit(battery_status_word, 7)

            # If true in DISCHARGE / RELAX MODE, else CHARGE
            battery_status['DSG'] = self.get_bit(battery_status_word, 6)

            # Fully charged
            battery_status['FC'] = self.get_bit(battery_status_word, 5)

            # Fully discharged
            battery_status['FD'] = self.get_bit(battery_status_word, 4)

            status = battery_status_word & 0b111

            if status == 0:
                battery_status['status'] = 'OK'
            elif status == 1:
                battery_status['status'] = 'BUSY'
            elif status == 2:
                battery_status['status'] = 'RSVD'
            elif status == 3:
                battery_status['status'] = 'unsupported'
            elif status == 4:
                battery_status['status'] = 'access denied'
            elif status == 5:
                battery_status['status'] = 'overflow/underflow'

        return battery_status


    def get_safety_status(self):
        safety_status_block = self.read_block_mac(SAFETYSTATUS_CMD)
        safety_status = dict()

        if safety_status_block:
            # Undertemperature during Discharge
            safety_status['UTD'] = self.get_bit(safety_status_block[0], 3)

            # Undertemperature during Charge
            safety_status['UTC'] = self.get_bit(safety_status_block[0], 2)

            # Over-Precharge Current
            safety_status['PCHGC'] = self.get_bit(safety_status_block[0], 1)

            # Overcharging voltage
            safety_status['CHGV'] = self.get_bit(safety_status_block[0], 0)

            # Overcharging current
            safety_status['CHGC'] = self.get_bit(safety_status_block[1], 7)

            # Overcharge
            safety_status['OC'] = self.get_bit(safety_status_block[1], 6)

            # Charge Timeout
            safety_status['CTO'] = self.get_bit(safety_status_block[1], 4)

            # Precharge Timeout
            safety_status['PTO'] = self.get_bit(safety_status_block[1], 2)

            # Overtemperature FET
            safety_status['OTF'] = self.get_bit(safety_status_block[1], 0)

            # Cell Undervoltage Compensated
            safety_status['CUVC'] = self.get_bit(safety_status_block[2], 6)

            # Overtemperature during discharge
            safety_status['OTD'] = self.get_bit(safety_status_block[2], 5)

            # Overtemperature during charge
            safety_status['OTC'] = self.get_bit(safety_status_block[2], 4)

            # Short-circuit during discharge latch
            safety_status['ASCDL'] = self.get_bit(safety_status_block[2], 3)

            # Short-circuit during discharge
            safety_status['ASCD'] = self.get_bit(safety_status_block[2], 2)

            # Short-circuit during during charge latch
            safety_status['ASCCL'] = self.get_bit(safety_status_block[2], 1)

            # Short-circuit during charge
            safety_status['ASCC'] = self.get_bit(safety_status_block[2], 0)

            # Overload during discharge latch
            safety_status['AOLDL'] = self.get_bit(safety_status_block[3], 7)

            # Overload during discharge
            safety_status['AOLD'] = self.get_bit(safety_status_block[3], 6)

            # Overcurrent during discharge 2
            safety_status['OCD2'] = self.get_bit(safety_status_block[3], 5)

            # Overcurrent during discharge 1
            safety_status['OCD1'] = self.get_bit(safety_status_block[3], 4)

            # Overcurrent during charge 2
            safety_status['OCC2'] = self.get_bit(safety_status_block[3], 3)

            # Overcurrent during charge 1
            safety_status['OCC1'] = self.get_bit(safety_status_block[3], 2)

            # Cell overvoltage
            safety_status['COV'] = self.get_bit(safety_status_block[3], 1)

            # Cell undervoltage
            safety_status['CUV'] = self.get_bit(safety_status_block[3], 0)

        return safety_status

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
