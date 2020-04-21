import logging
import csv

from .utils import *
from . import ev2300

from array import array
from time import sleep, monotonic
from pathlib import Path

class BQ40Z50:
    def __init__(self):
        self.ev = ev2300.EV2300()
        self.ev.prepare()
        self.battery_dict = dict()
        self.battery_dict_ready = False
        self.logger = logging.getLogger()

    def create_monitor(self, file_str):
        # Prepare log file
        log_path = Path(file_str)

        # Create file if it doesn't exist'
        log_path.touch()

        # Prepare file, it needs to be empty
        f = log_path.open()
        content = f.readlines()
        if content:
            self.logger.error("Monitoring file is not empty, exiting")
            #return -1

        # Logging monitoring time setup
        LOG_FREQ = 1
        interval_ms = 1000.0/LOG_FREQ
        log_time_last_ms = self.get_time_ms()


        while(True):
            log_time_now_ms = self.get_time_ms()

            if log_time_now_ms > log_time_last_ms + interval_ms:
                log_time_last_ms = log_time_now_ms

                # Query the data
                self.get_log()

                # Write into file
                self.write_log(f, log_time_now_ms)

    def get_log(self):
        # Add temperature
        temperature_dict = self.get_temperature()
        self.add_to_battery_dict(temperature_dict, "Temperature")

        # Add voltage
        voltage_dict = self.get_voltage()
        self.add_to_battery_dict(voltage_dict, "Voltage")

        # Add current
        current_dict = self.get_current()
        self.add_to_battery_dict(current_dict, "Current")

        # Add SOC
        soc_dict = self.get_soc()
        self.add_to_battery_dict(soc_dict, "SOC")

        # Add battery status
        battery_status_dict = self.get_battery_status()
        self.add_to_battery_dict(battery_status_dict, "Battery Status")

        # Add SOH
        soh_dict = self.get_soh()
        self.add_to_battery_dict(soh_dict, "SOH")

        # Add safety status
        safety_status_dict = self.get_safety_status()
        self.add_to_battery_dict(safety_status_dict, "Safety Status")

        # Add safety alert
        safety_alert_dict = self.get_safety_alert()
        self.add_to_battery_dict(safety_alert_dict, "Safety Alert")

        # Add PF status
        pf_status_dict = self.get_pf_status()
        self.add_to_battery_dict(pf_status_dict, "PF Status")

        # Add PF alert
        pf_alert_dict = self.get_pf_alert()
        self.add_to_battery_dict(pf_alert_dict, "PF Alert")

        # Add gauging status
        gauging_status_dict = self.get_gauging_status()
        self.add_to_battery_dict(gauging_status_dict, "Gauging Status")

        # Add lifetime 1 dict
        lifetime_1_dict = self.get_lifetime_1()
        self.add_to_battery_dict(lifetime_1_dict, "Lifetime 1")

        # Add lifetime 2 dict
        lifetime_2_dict = self.get_lifetime_2()
        self.add_to_battery_dict(lifetime_2_dict, "Lifetime 2")

        # Add lifetime 3 dict
        lifetime_3_dict = self.get_lifetime_3()
        self.add_to_battery_dict(lifetime_3_dict, "Lifetime 3")

        # Add lifetime 4 dict
        lifetime_4_dict = self.get_lifetime_4()
        self.add_to_battery_dict(lifetime_4_dict, "Lifetime 4")

        # Add lifetime 5 dict
        lifetime_5_dict = self.get_lifetime_5()
        self.add_to_battery_dict(lifetime_5_dict, "Lifetime 5")

        # Add DAStatus1
        dastatus1_dict = self.get_da_status1()
        self.add_to_battery_dict(dastatus1_dict, "DAStatus1")

        # Add DAStatus2
        dastatus2_dict = self.get_da_status2()
        self.add_to_battery_dict(dastatus2_dict, "DAStatus2")

        # Add gauge status 1
        gauge_status_1 = self.get_gauge_status1()
        self.add_to_battery_dict(gauge_status_1, "GaugeStatus1")

    def write_log(self, f, time_now):
        print(self.battery_dict)

    def get_soh(self):
        soh_dict = dict()

        cycle_count_word = self.read_word(CYCLECOUNT_REG)
        if cycle_count_word:
            soh_dict["Cycle count"] = cycle_count_word

        soh_word = self.read_word(SOH_REG)
        if soh_word:
            soh_dict["SOH"] = soh_word

    def get_soc(self):
        soc_dict = dict()

        max_error_word = self.read_word(MAXERROR_REG)
        if max_error_word:
            soc_dict["Max Error"] = max_error_word

        relative_soc_word = self.read_word(RELATIVESOC_REG)
        if relative_soc_word:
            soc_dict["Relative SOC"] = relative_soc_word

        absolute_soc_word = self.read_word(ABSOLUTESOC_REG)
        if absolute_soc_word:
            soc_dict["Absolute SOC"] = absolute_soc_word

        remaining_cap_word = self.read_word(REMAININGCAPACITY_REG)
        if remaining_cap_word:
            soc_dict["Remaining capacity"] = remaining_cap_word

        full_charge_cap_word = self.read_word(FULLCHARGECAPACITY_REG)
        if full_charge_cap_word:
            soc_dict["Full charge capacity"] = full_charge_cap_word

        return soc_dict


    def get_voltage(self):
        voltage_dict = dict()

        voltage_word = self.read_word(VOLTAGE_REG)
        if voltage_word:
            voltage_dict["Voltage"] = voltage_word

        charging_voltage_word = self.read_word(CHARGINGVOLTAGE_REG)
        if charging_voltage_word:
            voltage_dict["Charging voltage"] = charging_voltage_word
        return voltage_dict

    def get_temperature(self):
        temperature_word = self.read_word(TEMPERATURE_REG)
        temperature_dict = dict()

        if not temperature_word == DEFAULT_NA:
            # Convert to celsius
            temperature_word = temperature_word/10.0 - 273.15

        temperature_dict["Temperature"] = temperature_word

        return temperature_dict

    def get_current(self):
        current_dict = dict()

        current_word = self.read_word(CURRENT_REG)
        if current_word:
            current_dict["Current"] = current_word

        average_current_word = self.read_word(AVERAGECURRENT_REG)
        if average_current_word:
            current_dict["Average current"] = average_current_word

        charging_current_word = self.read_word(CHARGINGCURRENT_REG)
        if charging_current_word:
            current_dict["Charging current"] = charging_current_word

        return current_dict

    def create_summary(self):
        # TODO: change file handling to csv for all below methods
        while True:
            # Get existing data from battery_data.csv
            self.prepare_csv()

            # Get summary into battery_dict
            self.get_summary()

            # Write battery_dict into file
            self.write_summary()

            inp = input("Press ENTER for next battery")

    def write_summary(self):
        f = open(DATA_FILE, "a")

        # If the csv is empty we need to write keys first
        if not self.battery_dict_ready:
            # Set header len
            self.HEADER_LEN = len(self.battery_dict.keys())
            # Go through all fields
            for key in self.battery_dict.keys():
                f.write(key + ", ")

            # Newline after header
            f.write("\n")

        if not len(self.battery_dict.keys()) == self.HEADER_LEN:
            self.logger.error("HEADER_LEN not matching")
            return 1

        # Write data
        for key in self.battery_dict.keys():
            f.write(str(self.battery_dict[key]) + ", ")

        # Newline after data
        f.write("\n")

        f.close()


    def prepare_csv(self):
        f = open(DATA_FILE, "r")
        file_content = f.readlines()
        f.close()

        if not len(file_content) == 0:
            self.battery_dict_ready = True
            self.HEADER_LEN = len(file_content[0].split(", ")) - 1

    def get_summary(self):
        # Add serial number
        serial_number_dict = self.get_serial_number()
        self.add_to_battery_dict(serial_number_dict, "Serial Number")

        # Add cycle count
        cycle_count_dict = self.get_cycle_count()
        self.add_to_battery_dict(cycle_count_dict, "Cycle Count")

        # Add SOH
        soh_dict = self.get_soh()
        self.add_to_battery_dict(soh_dict, "SOH")

        # Add lifetime 1 dict
        lifetime_1_dict = self.get_lifetime_1()
        self.add_to_battery_dict(lifetime_1_dict, "Lifetime 1")

        # Add lifetime 2 dict
        lifetime_2_dict = self.get_lifetime_2()
        self.add_to_battery_dict(lifetime_2_dict, "Lifetime 2")

        # Add lifetime 3 dict
        lifetime_3_dict = self.get_lifetime_3()
        self.add_to_battery_dict(lifetime_3_dict, "Lifetime 3")

        # Add lifetime 4 dict
        lifetime_4_dict = self.get_lifetime_4()
        self.add_to_battery_dict(lifetime_4_dict, "Lifetime 4")

        # Add lifetime 5 dict
        lifetime_5_dict = self.get_lifetime_5()
        self.add_to_battery_dict(lifetime_5_dict, "Lifetime 5")

        # Add safety status
        safety_status_dict = self.get_safety_status()
        self.add_to_battery_dict(safety_status_dict, "Safety Status")

        # Add battery status
        battery_status_dict = self.get_battery_status()
        self.add_to_battery_dict(battery_status_dict, "Battery Status")

        # Add operation status
        operation_status_dict = self.get_operation_status()
        self.add_to_battery_dict(operation_status_dict, "Operation Status")

        # Add PF status
        pf_status_dict = self.get_pf_status()
        self.add_to_battery_dict(pf_status_dict, "PF Status")

        # Add gauging status
        gauging_status_dict = self.get_gauging_status()
        self.add_to_battery_dict(gauging_status_dict, "Gauging Status")

        # Add gauge status 1
        gauge_status_1 = self.get_gauge_status1()
        self.add_to_battery_dict(gauge_status_1, "GaugeStatus1")

    def add_to_battery_dict(self, result_dict: dict, topic_name: str):
        for key in result_dict.keys():
            field_name = topic_name + ": " + key

            # Add data
            self.battery_dict[topic_name + ": " + key] = result_dict[key]

    def read_block_mac(self, CMD: array) -> array:
        self.ev.smbus_write_block(DEV_ADDR, MAC_REG, CMD)
        block = self.ev.smbus_read_block(DEV_ADDR, MAC_REG)

        if block:
            # First two block words need to be the command
            if len(CMD) > 1 and not block[0] == CMD[0] and not block[1] == CMD[1]:
                self.logger.warning("Read block CMD not correct")
                # return None
            else:
                # Remove the cmd from the output block
                block.pop(0)
                block.pop(0)
        else:
            self.logger.error("Could not read MAC block")

        # Return as array object
        return block

    def read_block(self, CODE: array) -> array:
        return self.ev.smbus_read_block(DEV_ADDR, CODE)

    def read_word(self, REG: int):
        word = self.ev.smbus_read_word(DEV_ADDR, REG)
        if word:
            return word
        return DEFAULT_NA

    def bytes_to_str(self, input_b: bytes, l: int) -> str:
        output_str = ''
        for i in range(l):
            output_str += '{:08b}'.format(input_b[i])
        return output_str

    def get_bit(self, input_b: bytes, index: int) -> int:
        return (input_b >> index) & 1

    @staticmethod
    def get_time_ms():
        # https://www.python.org/dev/peps/pep-0418/#time-monotonic
        return int(round(monotonic() * 1000))

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

    def get_cycle_count(self) -> dict:
        cycle_count_word = self.read_word(CYCLECOUNT_REG)
        cycle_count = dict()

        if cycle_count_word:
            cycle_count["Cycle count"] = cycle_count_word
        return cycle_count

    def get_soh(self) -> dict:
        soh_word = self.read_word(SOH_REG)
        soh = dict()

        if soh_word:
            soh["SOH"] = soh_word
        return soh

    def get_serial_number(self) -> dict:
        serial_number_block = self.read_block(DEVICENAME_REG)
        serial_number = dict()

        if serial_number_block:
            serial_number["Serial Number 1"] = serial_number_block.tobytes().decode('utf-8').split(';')[0]
            serial_number["Serial Number 2"] = serial_number_block.tobytes().decode('utf-8').split(';')[1]

        return serial_number

    def get_gauge_status1(self):
        gauge_status_block = self.read_block_mac(GAUGINGSTATUS1_CMD)
        gauge_status = dict()

        if gauge_status_block:
            # True Rem Q
            gauge_status['True Rem Q'] = (gauge_status_block[1] << 8) | gauge_status_block[0]

            # True Rem E
            gauge_status['True Rem E'] = (gauge_status_block[3] << 8) | gauge_status_block[2]

            # Initial Q
            gauge_status['Initial Q'] = (gauge_status_block[5] << 8) | gauge_status_block[4]

            # Initial E
            gauge_status['Initial E'] = (gauge_status_block[7] << 8) | gauge_status_block[6]

            # True FCC Q
            gauge_status['True FCC Q'] = (gauge_status_block[9] << 8) | gauge_status_block[8]

            # True FCC E
            gauge_status['True FCC E'] = (gauge_status_block[11] << 8) | gauge_status_block[10]

            # T_sim, temperature during last simulation run
            gauge_status['T_sim'] = (gauge_status_block[13] << 8) | gauge_status_block[12]

            # T_ambient, current assumed ambient temperature
            gauge_status['T_ambient'] = (gauge_status_block[15] << 8) | gauge_status_block[14]

            # Ra Scale 0
            gauge_status['Ra Scale 0'] = (gauge_status_block[17] << 8) | gauge_status_block[16]

            # Ra Scale 1
            gauge_status['Ra Scale 1'] = (gauge_status_block[19] << 8) | gauge_status_block[18]

            # Ra Scale 2
            gauge_status['Ra Scale 2'] = (gauge_status_block[21] << 8) | gauge_status_block[20]

            # Ra Scale 3
            gauge_status['Ra Scale 3'] = (gauge_status_block[23] << 8) | gauge_status_block[22]

            # Comp Res 0
            gauge_status['Comp Res 0'] = (gauge_status_block[25] << 8) | gauge_status_block[24]

            # Comp Res 1
            gauge_status['Comp Res 1'] = (gauge_status_block[27] << 8) | gauge_status_block[26]

            # Comp Res 2
            gauge_status['Comp Res 2'] = (gauge_status_block[29] << 8) | gauge_status_block[28]

            # Comp Res 3
            gauge_status['Comp Res 3'] = (gauge_status_block[31] << 8) | gauge_status_block[30]

        return gauge_status

    def get_da_status1(self):
        da_status_block = self.read_block_mac(DASTATUS1_CMD)
        da_status = dict()

        if da_status_block:
            # Cell voltage 1
            da_status['Cell voltage 1'] = (da_status_block[1] << 8) | da_status_block[0]

            # Cell voltage 2
            da_status['Cell voltage 2'] = (da_status_block[3] << 8) | da_status_block[2]

            # Cell voltage 3
            da_status['Cell voltage 3'] = (da_status_block[5] << 8) | da_status_block[4]

            # Cell voltage 4
            da_status['Cell voltage 4'] = (da_status_block[7] << 8) | da_status_block[6]

            # BAT voltage (really measured, not just sum)
            da_status['BAT voltage'] = (da_status_block[9] << 8) | da_status_block[8]

            # Pack voltage
            da_status['Pack voltage'] = (da_status_block[11] << 8) | da_status_block[10]

            # Cell current 1
            da_status['Cell current 1'] = (da_status_block[13] << 8) | da_status_block[12]

            # Cell current 2
            da_status['Cell current 2'] = (da_status_block[15] << 8) | da_status_block[14]

            # Cell current 3
            da_status['Cell current 3'] = (da_status_block[17] << 8) | da_status_block[16]

            # Cell current 4
            da_status['Cell current 4'] = (da_status_block[19] << 8) | da_status_block[18]

            # Cell power 1
            da_status['Cell power 1'] = (da_status_block[21] << 8) | da_status_block[20]

            # Cell power 2
            da_status['Cell power 2'] = (da_status_block[23] << 8) | da_status_block[22]

            # Cell power 3
            da_status['Cell power 3'] = (da_status_block[25] << 8) | da_status_block[24]

            # Cell power 4
            da_status['Cell power 4'] = (da_status_block[27] << 8) | da_status_block[26]

            # Power voltage() * current()
            da_status['Power'] = (da_status_block[29] << 8) | da_status_block[28]

            # Average power
            da_status['Avg power'] = (da_status_block[31] << 8) | da_status_block[30]

        return da_status

    def get_da_status2(self):
        da_status_block = self.read_block_mac(DASTATUS2_CMD)
        da_status = dict()

        if da_status_block:
            # Int temperature
            da_status['Int temperature'] = (da_status_block[1] << 8) | da_status_block[0]

            # TS1 Temperature
            da_status['TS1 temperature'] = (da_status_block[3] << 8) | da_status_block[2]

            # TS2 Temperature
            da_status['TS2 temperature'] = (da_status_block[5] << 8) | da_status_block[4]

            # TS3 Temperature
            da_status['TS3 temperature'] = (da_status_block[7] << 8) | da_status_block[6]

            # TS4 Temperature
            da_status['TS4 temperature'] = (da_status_block[9] << 8) | da_status_block[8]

            # Cell Temperature
            da_status['Cell temperature'] = (da_status_block[11] << 8) | da_status_block[10]

            # FET Temperature
            da_status['FET temperature'] = (da_status_block[13] << 8) | da_status_block[12]

        return da_status

    def get_gauging_status(self):
        gauging_status_block = self.read_block_mac(GAUGINGSTATUS_CMD)
        gauging_status = dict()

        if gauging_status_block:
            # Open circuit voltage in flat region during relax
            gauging_status['OCVFR'] = self.get_bit(gauging_status_block[0], 4)

            # LOAD MODE
            gauging_status['LDMD'] = self.get_bit(gauging_status_block[0], 3)

            # resistance update
            gauging_status['RX'] = self.get_bit(gauging_status_block[0], 2)

            # qmax update
            gauging_status['QMax'] = self.get_bit(gauging_status_block[0], 1)

            # Discharge qualified for learning
            gauging_status['VDQ'] = self.get_bit(gauging_status_block[0], 0)

            # Negative scale factor mode
            gauging_status['NSFM'] = self.get_bit(gauging_status_block[1], 7)

            # OCV update in sleep mode
            gauging_status['SLPQMax'] = self.get_bit(gauging_status_block[1], 5)

            # Impedance track gauging (Ra and Qmax update are enabled)
            gauging_status['QEN'] = self.get_bit(gauging_status_block[1], 4)

            # Voltage are ok for QMax update
            gauging_status['VOK'] = self.get_bit(gauging_status_block[1], 3)

            # Resistance updates
            gauging_status['R_DIS'] = self.get_bit(gauging_status_block[1], 2)

            # Rest, 1: OCV Reading taken, 0: OCV Reading not taken or not in relax
            gauging_status['REST'] = self.get_bit(gauging_status_block[1], 1)

            # Condition flag, 1: MaxError > Max Error Limit, 0: <
            gauging_status['CF'] = self.get_bit(gauging_status_block[2], 7)

            # Discharge / relax
            gauging_status['DSG'] = self.get_bit(gauging_status_block[2], 6)

            # End of discharge termination voltage
            gauging_status['EDV'] = self.get_bit(gauging_status_block[2], 5)

            # Cell balancing
            gauging_status['BAL_EN'] = self.get_bit(gauging_status_block[2], 4)

            # Terminate charge
            gauging_status['TC'] = self.get_bit(gauging_status_block[2], 3)

            # Terminate discharge
            gauging_status['TD'] = self.get_bit(gauging_status_block[2], 2)

            # Fully charged
            gauging_status['FC'] = self.get_bit(gauging_status_block[2], 1)

            # Fully discharged
            gauging_status['FD'] = self.get_bit(gauging_status_block[2], 0)

        return gauging_status


    def get_pf_alert(self):
        pf_alert_block = self.read_block_mac(PFALERT_CMD)
        pf_alert = dict()

        if pf_alert_block:
            # Open Thermistor TS4 Failure
            pf_alert['TS4'] = self.get_bit(pf_alert_block[0], 7)

            # Open Thermistor TS3 Failure
            pf_alert['TS3'] = self.get_bit(pf_alert_block[0], 6)

            # Open Thermistor TS2 Failure
            pf_alert['TS2'] = self.get_bit(pf_alert_block[0], 5)

            # Open Thermistor TS1 Failure
            pf_alert['TS1'] = self.get_bit(pf_alert_block[0], 4)

            # Data flash wearout failure
            pf_alert['DFW'] = self.get_bit(pf_alert_block[0], 2)

            # Open cell tab connection failure
            pf_alert['OPNCELL'] = self.get_bit(pf_alert_block[0], 1)

            # Instruction flash checksum failure
            pf_alert['IFC'] = self.get_bit(pf_alert_block[0], 0)

            # PTC failure
            pf_alert['PTC'] = self.get_bit(pf_alert_block[1], 7)

            # Second level protector failure
            pf_alert['2LVL'] = self.get_bit(pf_alert_block[1], 6)

            # AFE communication failure
            pf_alert['AFEC'] = self.get_bit(pf_alert_block[1], 5)

            # AFE register failure
            pf_alert['AFER'] = self.get_bit(pf_alert_block[1], 4)

            # Chemical fuse failure
            pf_alert['FUSE'] = self.get_bit(pf_alert_block[1], 3)

            # Disharge FET failure
            pf_alert['DFETF'] = self.get_bit(pf_alert_block[1], 1)

            # Charge FET failure
            pf_alert['CFETF'] = self.get_bit(pf_alert_block[1], 0)

            # Voltage imbalance while pack is active failure
            pf_alert['VIMA'] = self.get_bit(pf_alert_block[2], 4)

            # Voltage imbalance while pack is at rest failure
            pf_alert['VIMR'] = self.get_bit(pf_alert_block[2], 3)

            # Capacity degradation failure
            pf_alert['CD'] = self.get_bit(pf_alert_block[2], 2)

            # Impedance failure
            pf_alert['IMP'] = self.get_bit(pf_alert_block[2], 1)

            # Cell balancing failure
            pf_alert['CB'] = self.get_bit(pf_alert_block[2], 0)

            # QMax imbalance failure
            pf_alert['QIM'] = self.get_bit(pf_alert_block[3], 7)

            # Safety overtemperature FET failure
            pf_alert['SOTF'] = self.get_bit(pf_alert_block[3], 6)

            # Safety overtemperature cell failure
            pf_alert['SOT'] = self.get_bit(pf_alert_block[3], 4)

            # Safety over current in discharge
            pf_alert['SOCD'] = self.get_bit(pf_alert_block[3], 3)

            # Safety overrcurrent in charge
            pf_alert['SOCC'] = self.get_operation_status(pf_alert_block[3], 2)

            # Safety cell overvoltage failure
            pf_alert['SOV'] = self.get_bit(pf_alert_block[3], 1)

            # Safety cell undervoltage failure
            pf_alert['SUV'] = self.get_bit(pf_alert_block[3], 0)

    def get_pf_status(self):
        pf_status_block = self.read_block_mac(PFSTATUS_CMD)
        pf_status = dict()

        if pf_status_block:
            # Open Thermistor TS4 Failure
            pf_status['TS4'] = self.get_bit(pf_status_block[0], 7)

            # Open Thermistor TS3 Failure
            pf_status['TS3'] = self.get_bit(pf_status_block[0], 6)

            # Open Thermistor TS2 Failure
            pf_status['TS2'] = self.get_bit(pf_status_block[0], 5)

            # Open Thermistor TS1 Failure
            pf_status['TS1'] = self.get_bit(pf_status_block[0], 4)

            # Data flash wearout failure
            pf_status['DFW'] = self.get_bit(pf_status_block[0], 2)

            # Open cell tab connection failure
            pf_status['OPNCELL'] = self.get_bit(pf_status_block[0], 1)

            # Instruction flash checksum failure
            pf_status['IFC'] = self.get_bit(pf_status_block[0], 0)

            # PTC failure
            pf_status['PTC'] = self.get_bit(pf_status_block[1], 7)

            # Second level protector failure
            pf_status['2LVL'] = self.get_bit(pf_status_block[1], 6)

            # AFE communication failure
            pf_status['AFEC'] = self.get_bit(pf_status_block[1], 5)

            # AFE register failure
            pf_status['AFER'] = self.get_bit(pf_status_block[1], 4)

            # Chemical fuse failure
            pf_status['FUSE'] = self.get_bit(pf_status_block[1], 3)

            # Disharge FET failure
            pf_status['DFETF'] = self.get_bit(pf_status_block[1], 1)

            # Charge FET failure
            pf_status['CFETF'] = self.get_bit(pf_status_block[1], 0)

            # Voltage imbalance while pack is active failure
            pf_status['VIMA'] = self.get_bit(pf_status_block[2], 4)

            # Voltage imbalance while pack is at rest failure
            pf_status['VIMR'] = self.get_bit(pf_status_block[2], 3)

            # Capacity degradation failure
            pf_status['CD'] = self.get_bit(pf_status_block[2], 2)

            # Impedance failure
            pf_status['IMP'] = self.get_bit(pf_status_block[2], 1)

            # Cell balancing failure
            pf_status['CB'] = self.get_bit(pf_status_block[2], 0)

            # QMax imbalance failure
            pf_status['QIM'] = self.get_bit(pf_status_block[3], 7)

            # Safety overtemperature FET failure
            pf_status['SOTF'] = self.get_bit(pf_status_block[3], 6)

            # Safety overtemperature cell failure
            pf_status['SOT'] = self.get_bit(pf_status_block[3], 4)

            # Safety over current in discharge
            pf_status['SOCD'] = self.get_bit(pf_status_block[3], 3)

            # Safety overrcurrent in charge
            pf_status['SOCC'] = self.get_operation_status(pf_status_block[3], 2)

            # Safety cell overvoltage failure
            pf_status['SOV'] = self.get_bit(pf_status_block[3], 1)

            # Safety cell undervoltage failure
            pf_status['SUV'] = self.get_bit(pf_status_block[3], 0)

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

    def get_safety_alert(self):
        safety_alert_block = self.read_block_mac(SAFETYALERT_CMD)
        safety_alert = dict()

        if safety_status_block:
            # Undertemperature during Discharge
            safety_alert['UTD'] = self.get_bit(safety_alert_block[0], 3)

            # Undertemperature during Charge
            safety_alert['UTC'] = self.get_bit(safety_alert_block[0], 2)

            # Over-Precharge Current
            safety_alert['PCHGC'] = self.get_bit(safety_alert_block[0], 1)

            # Overcharging voltage
            safety_alert['CHGV'] = self.get_bit(safety_alert_block[0], 0)

            # Overcharging current
            safety_alert['CHGC'] = self.get_bit(safety_alert_block[1], 7)

            # Overcharge
            safety_alert['OC'] = self.get_bit(safety_alert_block[1], 6)

            # Charge Timeout
            safety_alert['CTO'] = self.get_bit(safety_alert_block[1], 4)

            # Precharge Timeout
            safety_alert['PTO'] = self.get_bit(safety_alert_block[1], 2)

            # Overtemperature FET
            safety_alert['OTF'] = self.get_bit(safety_alert_block[1], 0)

            # Cell Undervoltage Compensated
            safety_alert['CUVC'] = self.get_bit(safety_alert_block[2], 6)

            # Overtemperature during discharge
            safety_alert['OTD'] = self.get_bit(safety_alert_block[2], 5)

            # Overtemperature during charge
            safety_alert['OTC'] = self.get_bit(safety_alert_block[2], 4)

            # Short-circuit during discharge latch
            safety_alert['ASCDL'] = self.get_bit(safety_alert_block[2], 3)

            # Short-circuit during discharge
            safety_alert['ASCD'] = self.get_bit(safety_alert_block[2], 2)

            # Short-circuit during during charge latch
            safety_alert['ASCCL'] = self.get_bit(safety_alert_block[2], 1)

            # Short-circuit during charge
            safety_alert['ASCC'] = self.get_bit(safety_alert_block[2], 0)

            # Overload during discharge latch
            safety_alert['AOLDL'] = self.get_bit(safety_alert_block[3], 7)

            # Overload during discharge
            safety_alert['AOLD'] = self.get_bit(safety_alert_block[3], 6)

            # Overcurrent during discharge 2
            safety_alert['OCD2'] = self.get_bit(safety_alert_block[3], 5)

            # Overcurrent during discharge 1
            safety_alert['OCD1'] = self.get_bit(safety_alert_block[3], 4)

            # Overcurrent during charge 2
            safety_alert['OCC2'] = self.get_bit(safety_alert_block[3], 3)

            # Overcurrent during charge 1
            safety_alert['OCC1'] = self.get_bit(safety_alert_block[3], 2)

            # Cell overvoltage
            safety_alert['COV'] = self.get_bit(safety_alert_block[3], 1)

            # Cell undervoltage
            safety_alert['CUV'] = self.get_bit(safety_alert_block[3], 0)

        return safety_alert


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
