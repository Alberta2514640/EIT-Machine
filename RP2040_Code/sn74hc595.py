# Wrapper function for writing to the Texas Instruments SN74HC595 shift registers on the 16CH-EIT board.
# Basically, we treat the SN74HC595 as a standard SPI MOSI device, since the latch pin and serial clock pin are connected.

# Function that takes a 16-bit value, splits it, and writes it to the shift register in the appropriate order.
# Unfortunately, the hardware design fails to account for the SPI being MSB First in CircuitPython.
# This means that we will have to convert our numbers, since writing 5 - 0101, will actually end up writing A - 1010.

import digitalio
import bitbangio
from board import *

import user_spi

def four_bit_swap(input:int):
    swapped = ((input & 0b0001) << 3) | ((input & 0b0010) << 1) | ((input & 0b0100) >> 1) | ((input & 0b1000) >> 3)
    byte = bytearray(1)
    byte[0] = swapped
    return byte

# We need to cycle an extra clock after the write. Unfortunately, this requires a deinit of the entire SR SPI.
# This function initializes the SPI bus, performs the transfer, then deinitializes it to perform a cycle on the clock signal.
# It appears that the SPI bus manager for CircuitPython is supposed to be able to do this, but I couldn't get it to work.
# See datasheet: Both the shift register clock (SRCLK) and storage register clock (RCLK) are positive-edge triggered. If both clocks are connected together, the shift register always is one clock pulse ahead of the storage register.
def sr_write (len:int, inputbuffer:bytearray):
    SPI_SR = bitbangio.SPI(GP14, GP15, None)
    SPI_SR.try_lock()
    SPI_SR.configure(baudrate=9600, polarity=0, phase=0, bits=8) # NOTE! Some baud rates here cause the Pico to enter an unrecoverable state!
    SPI_SR.unlock()

    user_spi.write(SPI_SR, None, len, inputbuffer)

    SPI_SR.deinit()
    clk = digitalio.DigitalInOut(GP14)
    clk.switch_to_output(True, drive_mode=digitalio.DriveMode.PUSH_PULL)
    clk.value = False
    clk.deinit ()
