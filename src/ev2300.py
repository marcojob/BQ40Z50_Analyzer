import usb.core
import usb.util
import struct
import crc8
import logging
import chromalog

from array import array
from time import sleep
from chromalog.mark.helpers.simple import success, error, important

chromalog.basicConfig(format="%(message)s", level=logging.DEBUG)
logger = logging.getLogger()

class EV2300:
    READ_WORD    = 0x01
    WRITE_WORD   = 0x04
    READ_BLOCK   = 0x02
    WRITE_BLOCK  = 0x05
    COMMAND	     = 0x06
    ERROR_CODE   = 0x46
    MAYBE_SUBMIT = 0x80

    def __init__(self):
        self.dev = None
        self.firmwareFilename = "resources/ev2300_default.bin"
        self.buffer = array('B', [0]) * 64

    def _load_firmware(self, dev):
        logger.info("Loading firmware: %s", important(self.firmwareFilename))
        firmware = array('B')
        with open(self.firmwareFilename, 'rb') as f:
            firmware.fromfile(f, 8073)
        header = array('B', b'\x89\x1f\x2b') # length_l, length_h, ?
        try:
            if dev.write(0x1, header + firmware[0:4093]) != 4096:
                return False
            if dev.write(0x1, firmware[4093:]) != 3980:
                return False
        except usb.core.USBError as e:
            logger.error("Firmware loading error: " + str(e))
        return True

    def _prepare(self):
        dev = usb.core.find(idVendor=0x0451, idProduct=0x0036) # flashed
        if dev is None:
            dev = usb.core.find(idVendor=0x0451, idProduct=0x2136) # empty
            if dev is None:
                logger.warning('EV2300 not connected, waiting...')
            else:
                dev.set_configuration()
                if self._load_firmware(dev):
                    logger.info('Firmware loaded, waiting...')
                    timeout = 5.0 #s
                    while timeout > 0:
                        dev = usb.core.find(idVendor=0x0451, idProduct=0x0036) # flashed
                        if dev is not None:
                            dev.set_configuration()
                            return dev
                        sleep(0.1)
                        timeout = timeout - 0.1
                    logger.error('EV2300 did note came back, will retry...')
                    return None
                else:
                    logger.error('Firmware loading failed, will retry...')
                    return None
        else:
            dev.set_configuration()
            return dev

    def prepare(self, timeout = 6.0):
        time_left = timeout
        while True:
            try:
                self.dev = self._prepare()
            except usb.core.USBError as e:
                if e.errno == 13:
                    logger.warning('Access denied, configure udev or run as root')
                    raise
            if self.dev is None:
                if timeout == 0:
                    return False
                elif timeout == None:
                    sleep(3.0)
                else:
                    time_left = time_left - 3.0
                    if time_left <= 0:
                        break
                    sleep(3.0)
            else:
                break
        if self.dev == None:
            logger.warning("Giving up waiting")
            return False
        else:
            logger.info("EV2300: %s", success("READY"))
            return True

    def _check_state(self):
        if self.dev == None:
            logger.warning('EV2300 not ready, call prepare() first')
            raise AssertionError('EV2300 not ready')

    def _check_arguments(self, device_address, register_address):
        if not (0 <= device_address <= 127):
            raise ValueError('Device address is invalid, should be (0-127)', device_address)
        if not (0 <= register_address <= 255):
            raise ValueError('Register address is invalid, should be (0-255)', register_address)

    def _calculate_crc(self, slice):
        crc = crc8.crc8()
        crc.update(slice.tostring())
        digest = array('B')
        digest.fromstring(crc.digest())
        return digest[0]

    def _fill_with_zeroes(self, after):
        self.buffer[after+1:64] = array('B', [0]) * (64 - after - 1)

    def _prepare_submit(self):
        self.buffer[0]    = 8
        self.buffer[1]    = 0xAA;
        self.buffer[2]    = self.MAYBE_SUBMIT
        self.buffer[3:6]  = array('B', [0]) * 3
        self.buffer[6]    = 0 # bytes till crc
        self.buffer[7]   = self._calculate_crc(self.buffer[2:7])
        self.buffer[8]   = 0x55
        self._fill_with_zeroes(self.buffer[0])

    def _request(self, timeout = 100, write_submit = False):
        try:
            self.dev.write(0x1, self.buffer, timeout)
            if write_submit:
                self._prepare_submit()
                self.dev.write(0x1, self.buffer, timeout)
            self.response = self.dev.read(0x81, 64, timeout)
            if len(self.response) != 64:
                logger.warning('Readed back length != 64', len(self.response))
                return False
            if self.response[2] == self.ERROR_CODE:
                logger.warning('Request error: {}'.format(self.response[2]))
                return False
            else:
                length = self.response[0]
                received_crc = self.response[length - 1]
                crc = self._calculate_crc(self.response[2:length-1])
                if crc != received_crc:
                    logger.warning('Received message CRC mismatch')
                    return False
                return True
        except usb.core.USBError as e:
            logger.warning("USB error: %s", str(e))
            return False

    def smbus_read_word(self, device_address, register_address):
        self._check_state()
        self._check_arguments(device_address, register_address)

        self.buffer[0] = 10 # total bytes except first
        self.buffer[1] = 0xAA;
        self.buffer[2] = self.READ_WORD
        self.buffer[3:6] = array('B', [0]) * 3
        self.buffer[6] = 2 # bytes till crc
        self.buffer[7] = device_address << 1
        self.buffer[8] = register_address
        self.buffer[9] = self._calculate_crc(self.buffer[2:9])
        self.buffer[10] = 0x55
        self._fill_with_zeroes(self.buffer[0]) # 11-63 bytes

        if not self._request():
            return None
        return struct.unpack('<H', self.response[8:10])[0]

    def smbus_write_word(self, device_address, register_address, word):
        self._check_state()
        self._check_arguments(device_address, register_address)
        if not (0 <= word <= 0xFFFF):
            raise ValueError('word not in range 0-FFFF', word)

        self.buffer[0] = 12 # total bytes except first
        self.buffer[1] = 0xAA;
        self.buffer[2] = self.WRITE_WORD
        self.buffer[3:6] = array('B', [0]) * 3
        self.buffer[6] = 4 # bytes till crc
        self.buffer[7] = device_address << 1
        self.buffer[8] = register_address
        self.buffer[9:11] = array('B', struct.pack('<H', word))
        self.buffer[11] = self._calculate_crc(self.buffer[2:11])
        self.buffer[12] = 0x55
        self._fill_with_zeroes(self.buffer[0])

        return self._request(write_submit = True)

    def smbus_read_block(self, device_address, block_address):
        self._check_state()
        self._check_arguments(device_address, block_address)

        self.buffer[0] = 10 # total bytes except first
        self.buffer[1] = 0xAA;
        self.buffer[2] = self.READ_BLOCK
        self.buffer[3:6] = array('B', [0]) * 3
        self.buffer[6] = 2 # bytes till crc
        self.buffer[7] = device_address << 1
        self.buffer[8] = block_address
        self.buffer[9] = self._calculate_crc(self.buffer[2:9])
        self.buffer[10] = 0x55
        self._fill_with_zeroes(self.buffer[0])

        if not self._request():
            return None
        block_length = self.response[8]
        return self.response[9:9+block_length]

    def smbus_write_block(self, device_address, block_address, block):
        self._check_state()
        self._check_arguments(device_address, block_address)
        if not (0 <= len(block) <= 52):
            raise ValueError('Block length not in range (0-52)', len(block))

        self.buffer[0] = 10+len(block)+1 # total bytes except first
        self.buffer[1] = 0xaa;
        self.buffer[2] = self.WRITE_BLOCK
        self.buffer[3:6] = array('B', [0]) * 3
        self.buffer[6] = len(block) + 3 # bytes till crc
        self.buffer[7] = device_address << 1
        self.buffer[8] = block_address
        self.buffer[9] = len(block)
        self.buffer[10:10+len(block)] = block
        self.buffer[10+len(block)] = self._calculate_crc(self.buffer[2:10+len(block)])
        self.buffer[10+len(block)+1]  = 0x55
        self._fill_with_zeroes(self.buffer[0])

        return self._request(write_submit = True)

    def smbus_command(self, device_address, command):
        self._check_state()
        if not (0 <= command <= 0xff):
            raise ValueError('Command number not in range 0-255', command)

        self.buffer[0] = 10 # total bytes except first
        self.buffer[1] = 0xAA;
        self.buffer[2] = self.COMMAND
        self.buffer[3:6] = array('B', [0]) * 3
        self.buffer[6] = 2 # bytes till crc
        self.buffer[7] = device_address << 1
        self.buffer[8] = command
        self.buffer[9] = self._calculate_crc(self.buffer[2:9])
        self.buffer[10] = 0x55
        self._fill_with_zeroes(self.buffer[0])

        return self._request(write_submit = True)