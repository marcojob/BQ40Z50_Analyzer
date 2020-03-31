from array import array
from time import sleep

from src import ev2300

def main():
    ev = ev2300.EV2300()
    ev.prepare()

    # Read voltages
    print(f"Cell 1 [mV]: {ev.smbus_read_word(0x0B, 0x3F)}")
    print(f"Cell 2 [mV]: {ev.smbus_read_word(0x0B, 0x3E)}")
    print(f"Cell 3 [mV]: {ev.smbus_read_word(0x0B, 0x3D)}")
    print(f"Cell 4 [mV]: {ev.smbus_read_word(0x0B, 0x3C)}")

    # Read total voltage
    print(f"Total [mV]: {ev.smbus_read_word(0x0B, 0x09)}")

    # Read current
    print(f"Current [mA]: {ev.smbus_read_word(0x0B, 0x0A)}")

    # Read temperature
    print(f"Temp [°C]: {ev.smbus_read_word(0x0B, 0x08)/100.0}")

    ev.smbus_write_block(0x0B, 0x44, array('B', b'\x06\x00'))
    print(f"Chem ID []: {ev.smbus_read_block(0x0B, 0x44)}")

if __name__ == "__main__":
    main()