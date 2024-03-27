# Functions for interacting with Analog Devices AD7680 analog to digital converters.

import busio
import digitalio
from board import *

import user_spi

# Function that does a one-shot 24-bit (3 8-bit word) conversion, discards the 4 leading and 4 trailing bits.
# Returns the formatted 16-bit value that is received by the ADC. The host will convert it to a floating-point number
# since the RP2040 doesn't have a dedicated FPU.
# Hopefully, this could mean that we can have really fast reconstructions, approaching real-time.
def single_conv (spi:busio.SPI, cs:digitalio.DigitalInOut, outbuffer:bytearray):
    if user_spi.user_try_lock(spi, cs):
        outbuffer = bytearray(3)
        user_spi.read(spi, cs, 3, outbuffer)
    else:
        print ("Failed to read from SPI)")
        return
    outval = ((outbuffer[0] & 0x0F)) << 12 | (outbuffer[1] << 4) | ((outbuffer[2] & 0xF0) >> 4)
    return outval