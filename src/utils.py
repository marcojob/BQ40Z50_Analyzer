""" Register definitions for BQ40Z50"""

from array import array

# General definitions
DATA_FILE = "battery_data.csv"
DEFAULT_NA = "N/A"

# Registers
DEV_ADDR = 0x0B # Device address
MAC_REG = 0x44 # Register of MAC

# Read word
TEMPERATURE_REG = 0x08
VOLTAGE_REG = 0x09
CURRENT_REG = 0x0A
AVERAGECURRENT_REG = 0x0B
MAXERROR_REG = 0x0C
RELATIVESOC_REG = 0x0D
ABSOLUTESOC_REG = 0x0E
REMAININGCAPACITY_REG = 0x0F
FULLCHARGECAPACITY_REG = 0x10
CHARGINGCURRENT_REG = 0x14
CHARGINGVOLTAGE_REG = 0x15
BATTERYSTATUS_REG = 0x16
CYCLECOUNT_REG = 0x17
CELLVOLTAGE4_REG = 0x3C
CELLVOLTAGE3_REG = 0x3D
CELLVOLTAGE2_REG = 0x3E
CELLVOLTAGE1_REG = 0x3F
SOH_REG = 0x4F

# Read block
DEVICENAME_REG = 0x21

# Manufacturer Access (MAC) Commands
# Available in SEALED Mode
SAFETYALERT_CMD = array('B', b'\x50\x00')
SAFETYSTATUS_CMD = array('B', b'\x51\x00')
PFALERT_CMD = array('B', b'\x52\x00')
PFSTATUS_CMD = array('B', b'\x53\x00')
OPERATIONSTATUS_CMD = array('B', b'\x54\x00')
GAUGINGSTATUS_CMD = array('B', b'\x55\x00')

LIFETIMEDATABLOCK1_CMD = array('B', b'\x60\x00')
LIFETIMEDATABLOCK2_CMD = array('B', b'\x61\x00')
LIFETIMEDATABLOCK3_CMD = array('B', b'\x62\x00')
LIFETIMEDATABLOCK4_CMD = array('B', b'\x63\x00')
LIFETIMEDATABLOCK5_CMD = array('B', b'\x64\x00')

DASTATUS1_CMD = array('B', b'\x71\x00')
DASTATUS2_CMD = array('B', b'\x72\x00')

GAUGESTATUS1_CMD = array('B', b'\x73\x00')
GAUGESTATUS2_CMD = array('B', b'\x74\x00')
GAUGESTATUS3_CMD = array('B', b'\x75\x00')

lifetime_1_thresholds = {'Cell 1 max mV': (2700, 4200),
                         'Cell 2 max mV': (2700, 4200),
                         'Cell 3 max mV': (2700, 4200),
                         'Cell 4 max mV': (2700, 4200),
                         'Cell 1 min mV': (2700, 4200),
                         'Cell 2 min mV': (2700, 4200),
                         'Cell 3 min mV': (2700, 4200),
                         'Cell 4 min mV': (2700, 4200),
                         'Max Delta Cell mV': (0, 250),
                         'Max Charge mA': 4037,
                         'Max Discharge mA': 37641,
                         'Max Avg Dsg mA': 47230,
                         'Max Avg Dsg mW': 41479,
                         'Max temp cell': 46,
                         'Min temp cell': 15,
                         'Max delta cell temp': (0, 10),
                         'Max Temp Int Sensor': 51,
                         'Min Temp Int Sensor': 13,
                         'Max Temp Fet': 61}
