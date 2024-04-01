# Wrapper function for writing to the Texas Instruments SN74HC595 shift registers on the 16CH-EIT board.
# Basically, we treat the SN74HC595 as a standard SPI MOSI device, since the latch pin and serial clock pin are connected.

# Function that takes a 16-bit value, splits it, and writes it to the shift register in the appropriate order.
# Unfortunately, the hardware design fails to account for the SPI being MSB First in CircuitPython.
# This means that we will have to convert our numbers, since writing 5 - 0101, will actually end up writing A - 1010.

import time
import digitalio
import bitbangio
from board import *

import user_spi

# Reverses the order of the bits in a 16-bit number. This is because the SPI sends MSB-first, but the shift register is wired LSB-first.
def bit_swap (input:int):
    swapped = ((input & 0b00000001) << 7) | ((input & 0b00000010) << 5) | ((input & 0b00000100) << 3) | ((input & 0b00001000) << 1) | ((input & 0b00010000) >> 1) | ((input & 0b00100000) >> 3) | ((input & 0b01000000) >> 5) | ((input & 0b10000000) >> 7)
    return swapped

# We need to cycle an extra clock after the write. Unfortunately, this requires a deinit of the entire SR SPI.
# This function clears the shift register, then writes to it. Disables the SPI and cycles it by one cycle.
# It appears that the SPI bus manager for CircuitPython is supposed to be able to do this, but I couldn't get it to work.
# See datasheet: Both the shift register clock (SRCLK) and storage register clock (RCLK) are positive-edge triggered. If both clocks are connected together, the shift register always is one clock pulse ahead of the storage register.
def sr_write (spi:bitbangio.SPI, lCLR:digitalio.DigitalInOut, lOE:digitalio.DigitalInOut, inputbuffer:bytearray):

    # Clear and disable output
    lCLR.value = False
    lOE.value = True
    time.sleep(0.1)
    lCLR.value = True

    user_spi.write(spi, None, len(inputbuffer), inputbuffer=inputbuffer)
    spi.deinit()
    clk = digitalio.DigitalInOut(GP14)
    clk.switch_to_output(False, drive_mode=digitalio.DriveMode.PUSH_PULL)
    clk.value = True
    clk.deinit ()
    spi = bitbangio.SPI(GP14, GP15, None)
    spi.try_lock()
    # NOTE! Some baud rates here cause the Pico to enter an unrecoverable state!
    # Originally tested with 9600 baud.
    spi.configure(baudrate=115200, polarity=0, phase=0, bits=9)
    spi.unlock()

    # Re-enable output
    lOE.value = False

# Wraps a whole shift register update cycle
def sr_update (spi:bitbangio.SPI, lCLR:digitalio.DigitalInOut, lOE:digitalio.DigitalInOut, source:int, sink:int, in_p:int, in_n:int):

    # Determine the register values based on what is given in the argument
    sink_hex   = sink & 0x0F
    in_n_hex   = in_n & 0x0F
    word1 = (sink_hex << 4) | in_n_hex

    in_p_hex   = in_p & 0x0F
    source_hex = source & 0x0F
    word2 = (in_p_hex << 4) | source_hex

    outputbuf = bytearray(2)
    outputbuf[0] = word1
    outputbuf[1] = word2

    sr_write (spi, lCLR, lOE, outputbuf)
