import time
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
import awg
import eit
import ad9512
import ad9106
import ad7680
import sn74hc595
import user_spi

# Misc. Control Signals
lSR_CLR   = digitalio.DigitalInOut(GP12)  # (GP12) ~SR_CLR
lSR_OE    = digitalio.DigitalInOut(GP13)  # (GP13) ~SR_OE
lDDS_SYNC = digitalio.DigitalInOut(GP16)  # (GP16) ~DDS SYNC
lAMP_PD   = digitalio.DigitalInOut(GP18)  # (GP18) ~AMP PD
lEIT_PD   = digitalio.DigitalInOut(GP19)  # (GP19) ~EIT PD
MUX_EN    = digitalio.DigitalInOut(GP20)  # (GP20) MUX EN

# SPI chip selects
lDDS1_CS   = digitalio.DigitalInOut(GP1 )  # (GP1 ) AD9106 #1 (DDS 1)
lDDS2_CS   = digitalio.DigitalInOut(GP5 )  # (GP5 ) AD9106 #2 (DDS 2)
lDDS3_CS   = digitalio.DigitalInOut(GP17)  # (GP17) AD9106 #3 (DDS 3)
lDDS4_CS   = digitalio.DigitalInOut(GP21)  # (GP21) AD9106 #4 (DDS 4)
lADC_CS    = digitalio.DigitalInOut(GP25)  # (GP25) AD7680 (ADC)
lCLKBUF_CS = digitalio.DigitalInOut(GP9 )  # (GP9 ) AD9512 (Clock Divider)

for pin in [ lSR_CLR, lSR_OE, lDDS_SYNC, lAMP_PD, lEIT_PD,
            lDDS1_CS, lDDS2_CS, lDDS3_CS, lDDS4_CS, lADC_CS, lCLKBUF_CS]:
    pin.switch_to_output(True, digitalio.DriveMode.PUSH_PULL)
MUX_EN.switch_to_output(False, digitalio.DriveMode.PUSH_PULL)

# Set up SPI interfaces (SCLK, MOSI, MISO)
# The CircuitPython SPIDevice library doesn't seem to work yet,
# meaning that we'll have to manage the locks ourselves.
SPI0 = busio.SPI(GP2, GP3, GP0)  # SPI 0
SPI1 = busio.SPI(GP10, GP11, GP8)  # SPI 1
SPI_SR = bitbangio.SPI(GP14, GP15, None)

SPI0.try_lock()
SPI1.try_lock()
SPI_SR.try_lock()

# All of our SPI devices fortunately use SPI mode 0.
SPI0.configure(baudrate=7812500, polarity=0, phase=0, bits=8)  # Highest supported baud rate on this port
SPI1.configure(baudrate=7812500, polarity=0, phase=0, bits=8)
SPI_SR.configure(baudrate=9600, polarity=0, phase=0, bits=9) # NOTE! Some baud rates here cause the Pico to enter an unrecoverable state!
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

# Run initialialization code for each device
# Default state: AWG mode with all channels disabled

print("Initialization complete, listening to data serial port for commands:\n")

# Main loop
while False:
    # This is crazy insecure, do NOT use this in real production code!
    if usb_cdc.data.in_waiting != 0:
        command = usb_cdc.data.readline() # Make sure that every command ends with a newline "\n"
        print("(DEBUG) Command received: (", command, "). Executing.")
        usb_cdc.data.flush()
        try:
            exec(command)
        except Exception as err:
            traceback.print_exception(err)

# DEBUG
# GP6 will be our temporary test pin
# Clear intermediate register by clocking the shift register during a shift register clear
TEST_PIN = digitalio.DigitalInOut(GP6)
TEST_PIN.switch_to_input(pull=digitalio.Pull.DOWN)
# The SPI transfers are broken up by 8-bit word.
# The MSB ends up being QH, while the LSB ends up being QA.
sn74hc595.sr_update (SPI_SR, lSR_CLR, lSR_OE, 15, 15, 15, 15)

while True:
    time.sleep(0.05)
    if TEST_PIN.value:
        print ("!!!")
    else:
        print ("...")

# TODO

# AD9512
# Write register initialization for the AD9512

# AD9106
# Write register initilaization for the AD9106
# Write wrapper function that implements settings changes to the channels
# Write low level functions that implement register changes in individual AD9106es

# EIT
# Write function that implements EIT

# AD7680
# Write function that takes a one-shot ADC reading