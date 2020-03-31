""" Register definitions for BQ40Z50"""

from array import array

# Device address
DEV_ADDR = 0x0B

# Manufacturer Access (MAC) Commands
MAC_REG = 0x44 # Register of MAC

# Available in SEALED Mode
CHEMID_CMD = array('B', b'\x06\x00')
OPERATIONSTATUS_CMD = array('B', b'\x54\x00')
