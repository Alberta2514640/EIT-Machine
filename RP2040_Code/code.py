import time
import busio
import rp2pio
import digitalio
import bitbangio
import adafruit_74hc595 as srio
import microcontroller
from board import *

# CircuitPython, by convention, uses GPIO number to refer to pins, rather than physical pin number.

# Misc. Control Signals
lSR_CLR   = digitalio.DigitalInOut(GP12) # (GP12) ~SR_CLR
lSR_OE    = digitalio.DigitalInOut(GP13) # (GP13) ~SR_OE
lDDS_SYNC = digitalio.DigitalInOut(GP16) # (GP16) ~DDS SYNC
lAMP_PD   = digitalio.DigitalInOut(GP18) # (GP18) ~AMP PD
lEIT_PD   = digitalio.DigitalInOut(GP19) # (GP19) ~EIT PD
MUX_EN    = digitalio.DigitalInOut(GP20) # (GP20) MUX EN

# SPI chip selects
lDDS1_CS   = digitalio.DigitalInOut(GP1)   # (GP1 ) AD9106 #1 (DDS 1)
lDDS2_CS   = digitalio.DigitalInOut(GP5)   # (GP5 ) AD9106 #2 (DDS 2)
lDDS3_CS   = digitalio.DigitalInOut(GP17)  # (GP17) AD9106 #3 (DDS 3)
lDDS4_CS   = digitalio.DigitalInOut(GP21)  # (GP21) AD9106 #4 (DDS 4)
lADC_CS    = digitalio.DigitalInOut(GP25)  # (GP25) AD7680 (ADC)
lCLKDIV_CS = digitalio.DigitalInOut(GP9)   # (GP9 ) AD9512 (Clock Divider)

pins = [lSR_CLR, lSR_OE, lDDS_SYNC, lAMP_PD, lEIT_PD, MUX_EN, lDDS1_CS,
        lDDS1_CS, lDDS2_CS, lDDS3_CS, lDDS4_CS, lADC_CS, lCLKDIV_CS]
for pin in pins:
    pin.switch_to_output(True, digitalio.DriveMode.PUSH_PULL)

# Set up SPI interfaces
SPI0 = busio.SPI(GP2, GP3, GP0) # SPI 0
SPI1 = busio.SPI(GP10, GP11, GP8) # SPI 1
SPI_SR = bitbangio.SPI(GP14, GP15, None) # SPI SR (Shift Register)

# Set up SN74HC595 (mux control shift register)ada
sr = srio.ShiftRegister74HC595 (SPI_SR, None, 2)
sr_pins = [sr.get_pin(n) for n in range(16)] # Array of OUTPUT pins that represent the outputs of the shift registers.

# Start sending out clock on uC_CLKOUT (GP23, PIO)

# Put each SPI device in reset

# Setup USB communications

# Main loop

# SPI Write Function Wrapper with CS

# SPI Read Function Wrapper with CS
