# -*- coding: utf-8 -*-
import ev2300

ev = ev2300.EV2300()
ev.prepare()

print(ev.smbus_read_word(0x40, 0x01))
print(ev.smbus_write_word(0x40, 0x01, 0))

block = ev.smbus_read_block(0x40, 0x99)
print(''.join('{:c} '.format(x) for x in block))

print(ev.smbus_write_block(0x40, 0x9d, b'\x01\x02\x03\x04\x05\x06'))

print(ev.smbus_command(0x40, 0x02))