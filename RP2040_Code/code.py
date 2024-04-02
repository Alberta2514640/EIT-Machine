import time
import array
import busio
import rp2pio
import digitalio
import bitbangio
import usb_cdc
import traceback
import microcontroller
import adafruit_pioasm
from adafruit_bus_device import spi_device
from board import *

# User drivers
# import awg
import ad9512
import ad9106
import user_serial

# To whoever is reading this in the future:
# This code is a mess, hobbled together last minute for capstone.
# Thank you for your understanding (*_ _)人

# Initialization code:

# Misc. Control Signals
lSR_CLR   = digitalio.DigitalInOut(GP12)  # (GP12) ~SR_CLR
lSR_OE    = digitalio.DigitalInOut(GP13)  # (GP13) ~SR_OE
lDDS_SYNC = digitalio.DigitalInOut(GP16)  # (GP16) ~DDS SYNC (Trigger)
lAMP_PD   = digitalio.DigitalInOut(GP18)  # (GP18) ~AMP PD (PD for all channels except for channel 1)
lEIT_PD   = digitalio.DigitalInOut(GP19)  # (GP19) ~EIT PD (PD for channel 1)
MUX_EN    = digitalio.DigitalInOut(GP20)  # (GP20) MUX EN

# SPI chip selects
# lDDS1_CS   = digitalio.DigitalInOut(GP1 )  # (GP1 ) AD9106 #1 (DDS 1) (Not populated on prototype board)
# lDDS2_CS   = digitalio.DigitalInOut(GP5 )  # (GP5 ) AD9106 #2 (DDS 2) (Not populated on prototype board)
# lDDS3_CS   = digitalio.DigitalInOut(GP17)  # (GP17) AD9106 #3 (DDS 3) (Not populated on prototype board)
lDDS4_CS   = digitalio.DigitalInOut(GP21)  # (GP21) AD9106 #4 (DDS 4)
lADC_CS    = digitalio.DigitalInOut(GP25)  # (GP25) AD7680 (ADC)
lCLKBUF_CS = digitalio.DigitalInOut(GP9 )  # (GP9 ) AD9512 (Clock Divider)

for pin in [ lSR_CLR, lSR_OE, lDDS_SYNC, lAMP_PD,
             lEIT_PD, lDDS4_CS, lADC_CS, lCLKBUF_CS]:
    pin.switch_to_output(True, digitalio.DriveMode.PUSH_PULL)
for pin in [ MUX_EN]:
    pin.switch_to_output(False, digitalio.DriveMode.PUSH_PULL)

# Set up SPI interfaces (SCLK, MOSI, MISO)
# The CircuitPython SPIDevice library doesn't seem to work yet,
# meaning that we'll have to manage the locks ourselves.
SPI0 = busio.SPI(GP2, GP3, GP0)  # SPI 0
SPI1 = busio.SPI(GP10, GP11, GP8)  # SPI 1
SPI_SR = bitbangio.SPI(GP14, GP15, None) # This should have been on its own interface. The bitbang SPI is much slower.

SPI0.try_lock()
SPI1.try_lock()
SPI_SR.try_lock()

# All of our SPI devices fortunately use SPI mode 0.
SPI0.configure(  baudrate=7812500, polarity=0, phase=0, bits=8)
SPI1.configure(  baudrate=7812500, polarity=0, phase=0, bits=8)
SPI_SR.configure(baudrate=921600 , polarity=0, phase=0, bits=9) # NOTE! Some baud rates here cause the Pico to enter an unrecoverable state!
                                                                # We need a 9th bit here because we must cycle the device one extra time.
SPI0.unlock()
SPI1.unlock()
SPI_SR.unlock()

# Start sending out a clock on uC_CLKOUT (GP23, PIO)
# The maximum clock we can use is theoretically 62.5 MHz
# In practice, anything above 12.5 MHz has some pretty crazy pulse distortion going on
# This could possibly be improved in the future by getting the clock signal out of
# the RP2040's CLOCK GPOUTx outputs, but it doesn't seem like CircuitPython has this ability.
cpu_freq = microcontroller.cpu.frequency / 1000000
print("Core is running at:", cpu_freq, " MHz")
clock_asm = adafruit_pioasm.assemble(
    """
    set pins, 0 [4]
    set pins, 1 [4]
"""
) # Results in a final clock of 12.5 MHz (125 MHz / 5 cycles on / 5 cycles off)
clock_pio_state_machine = rp2pio.StateMachine(clock_asm, frequency=0, first_set_pin=GP22)

# Serial port helper functions

def start_eit():
    user_serial.start_eit(SPI0, lADC_CS, SPI_SR, lSR_OE, lSR_CLR)
    pass
    # API hook for calling the EIT function

def update_awg(len):
    user_serial.update_awg(len)

# Run initialialization code for each device that require it (AD9512 then AD9106es)
ad9512.init(lCLKBUF_CS) # For now, it's okay for the CLKBUF to be left at default values.
ad9106.init(SPI0, lDDS_SYNC, lDDS4_CS)

# Main loop
# Listen for commands issued from the host computer
# EIT mode
# Change AWG setting
# Software reset (After software reset, execute init functions again)

lADC_CS.value = False
SPI0.try_lock()
outputbuffer = bytearray(3)
SPI0.readinto(outputbuffer)
for i in outputbuffer:
    print (i)
SPI0.unlock()
lADC_CS.value = True

lDDS4_CS.value = False
SPI0.try_lock()
# Check tuning word MSB
inputbuffer = bytearray([0x80, 0x3E])
SPI0.write(inputbuffer)
outputbuffer = bytearray(2)
SPI0.readinto(outputbuffer)
print (outputbuffer)
lDDS4_CS.value = True
lDDS4_CS.value = False
# Check tuning word LSB
inputbuffer = bytearray([0x80, 0x3F])
SPI0.write(inputbuffer)
outputbuffer = bytearray(2)
SPI0.readinto(outputbuffer)
print (outputbuffer)
lDDS4_CS.value = True
SPI0.unlock()

lCLKBUF_CS.value = False
inputbuffer = bytearray([0x80, 0x00])
SPI1.try_lock()
SPI1.write(inputbuffer)
outputbuffer = bytearray(1)
SPI1.readinto(outputbuffer)
print (outputbuffer)
SPI1.unlock()
lCLKBUF_CS.value = True

while True:
    print("Initialization complete, listening to data serial port for commands:\n")
    # This is crazy insecure, do NOT use this in real production code!
    while usb_cdc.data.in_waiting == 0:
        continue
    command = usb_cdc.data.readline() # Make sure that every command ends with a newline "\n"
    usb_cdc.data.flush()
    usb_cdc.data.reset_input_buffer()
    usb_cdc.data.reset_output_buffer()
    ack = bytearray([0x00])
    usb_cdc.data.write(ack)
    print("(DEBUG) Command received: (", command, "). Executing.")
    print("(DEBUG) Command size:", len(command))
    try:
        exec(command)
        usb_cdc.data.flush()
        usb_cdc.data.reset_input_buffer()
        usb_cdc.data.reset_output_buffer()
    except Exception as err:
        traceback.print_exception(err)

# DEBUG
''' (SN74HC595 test)
# GP6 will be our temporary test pin
# Clear intermediate register by clocking the shift register during a shift register clear
TEST_PIN = digitalio.DigitalInOut(GP6)
TEST_PIN.switch_to_input(pull=digitalio.Pull.DOWN)
# The SPI transfers are broken up by 8-bit word.
# The MSB ends up being QH, while the LSB ends up being QA.
sn74hc595.sr_update (SPI_SR, lSR_CLR, lSR_OE, 15, 15, 15, 15)
'''

''' (AD7680 test)
outbuffer = bytearray(3)
outbuffer[0] = 0x01
outbuffer[1] = 0x23
outbuffer[2] = 0x40
# Reconstruct a 16-bit word, stripping the leading and trailing zeroes.
outval = ((outbuffer[0] & 0x0F)) << 12 | (outbuffer[1] << 4) | ((outbuffer[2] & 0xF0) >> 4)
print(outval)
'''

while True:
    ''' (EIT Bulk serial send test)
    ex_mat_len = int.from_bytes(usb_cdc.data.read(1), "little")
    print(ex_mat_len)
    ex_mat_bytes = usb_cdc.data.read(ex_mat_len)
    print(ex_mat_bytes.hex())
    usb_cdc.data.reset_input_buffer()
    '''

