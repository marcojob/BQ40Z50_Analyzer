""" Register definitions for BQ40Z50"""

from array import array

# General definitions
DATA_FILE = "battery_data.csv"

# Registers
DEV_ADDR = 0x0B # Device address
MAC_REG = 0x44 # Register of MAC

# Read word
BATTERYSTATUS_REG = 0x16
CYCLECOUNT_REG = 0x17
SOH_REG = 0x4F

# Read block
DEVICENAME_REG = 0x21

# Manufacturer Access (MAC) Commands
# Available in SEALED Mode
SAFETYALERT_CMD = array('B', b'\x50\x00')
SAFETYSTATUS_CMD = array('B', b'\x51\x00')

OPERATIONSTATUS_CMD = array('B', b'\x54\x00')

LIFETIMEDATABLOCK1_CMD = array('B', b'\x60\x00')
LIFETIMEDATABLOCK2_CMD = array('B', b'\x61\x00')
LIFETIMEDATABLOCK3_CMD = array('B', b'\x62\x00')
LIFETIMEDATABLOCK4_CMD = array('B', b'\x63\x00')
LIFETIMEDATABLOCK5_CMD = array('B', b'\x64\x00')