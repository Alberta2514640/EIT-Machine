# Functions for interacting with Analog Devices AD7680 analog to digital converters.

import busio
import digitalio
from board import *

import user_spi

# Function that does a one-shot 24-bit (3 8-bit word) conversion, discards the 4 leading and 4 trailing bits.
# Returns the formatted 16-bit value that is received by the ADC. The host will convert it to a floating-point number
# since the RP2040 doesn't have a dedicated FPU.
# Hopefully, this could mean that we can have really fast reconstructions, approaching real-time.
def single_conv (spi:busio.SPI, cs:digitalio.DigitalInOut):
    spi.try_lock()
    cs.value = False
    buffer = bytearray(3)
    spi.readinto(buffer)
    # print (buffer)
    cs.value = True
    spi.unlock()
    # print (buffer[2])
    outval = (((buffer[0] & 0x0F)) << 12) | ((buffer[1] << 4)) | (((buffer[2] & 0xF0) >> 4))
    # print (outval)
    return outval