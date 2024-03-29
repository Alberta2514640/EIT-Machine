# Functions for interacting with Analog Devices AD9106 direct digital synthesis (DDS) ICs, that implement the AWG mode of the 16CH_EIT.

import digitalio

# Startup procedure
def init(trigger:digitalio.DigitalInOut, dds1_cs:digitalio.DigitalInOut, dds2_cs:digitalio.DigitalInOut, dds3_cs:digitalio.DigitalInOut, dds4_cs:digitalio.DigitalInOut):
    for cs in dds1_cs: #, dds2_cs, dds3_cs, dds4_cs: # Skip these since they're not populated on the prototype board
        # Raise trigger line to stop any pattern generation.
        # Set initialized non-default settings
        # Update SPI
        #
        pass
    pass

# Serial control format:
# All SPI transactions on the AD9106 are preceded by a 16-bit control word.
# 15: Read/Write Bit (0 Write, 1 Read) | 14-0: 15-Bit Register Base Address

# Subsequent read/write operations to the AD9106 SPI port are auto-incrementing in register space, and auto-decrementing in SRAM space.
# Register updates are stored in shadow registers until they are written to register memory by setting the self-clearing RAMUPDATE register (0x1D).
# SRAM Space occupies 0x6000 - 0x6FFF. SRAM updates are reflected immediately, but data is only written as long as pattern generation is off (RUN = 0)

# Top-level function that is called by the GUI to change AWG attributes.
# Individually calls other functions to adjust individual channel attributes

# Helper function that determines which DDS chip to send to

# Turn on/off channel

# Adjust channel (amplitude, frequency, phase, wave type)
# Adjusting any of these attributes requires rewriting to the SRAM and registers.
# To save effort in adjusting these manually, we'll just do blanket changes since change time is not critical.

# Register Map

## Configuration and Status
# 0x00 SPI Control
# 0x01 Power Status
# 0x02 Clock Control
# 0x03 Reference Resistor Register

## Analog Calibration
# 0x04 - 0x07 DACx DAC Analog Gain
# 0x08 DACx DAC Analog Gain Range
# 0x09 - 0x0C DACx FSADJx (R SET Resistor Control)
# 0x0D Calibration (CALCONFIG)
# 0x0E Comparator Offset

## Raise to update SPI registers
# 0x1D Update Pattern (RAM)

## Pattern Configuration
# 0x1E Command/Status (PAT_STATUS)
# 0x1F Command/Status (PAT_TYPE)
# 0x20 Trigger Start to Real Pattern Delay
# 0x22 - 0x25 DACx Digital Offset
# 0x26 Wave 4,3 Select
# 0x27 Wave 2,1 Select
# 0x28 DAC Time Control
# 0x29 Pattern Period
# 0x2A DAC 4,3 Pattern Repeat Cycle
# 0x2B DAC 2,1 Pattern Repeat Cycle
# 0x2C Trigger Start to DOUT Signal
# 0x2C DOUT Configuration
# 0x2E - 0x31 DACx Constant Value
# 0x32 - 0x35 DACx Digital Gain
# 0x36 DAC 4,3 Sawtooth Configuration
# 0x37 DAC 2,1 Sawtooth Configuration
# 0x3E DDS Tuning Word MSByte Register
# 0x3F DDS Tuning Word LSByte Register
# 0x40 - 0x43 DDSx Phase Offset
# 0x44 Pattern Control 1 (TRIG_TW_SEL)
# 0x45 Pattern Control 2 (DDSx_CONFIG)
# 0x47 TW_RAM_CONFIG (Tuning Word)

# 0x50 START DELAY 4
# 0x51 START ADDRESS 4
# 0x52 STOP ADDRESS 4
# 0x53 DDS CYCLE 4

# 0x54 START DELAY 3
# 0x55 START ADDRESS 3
# 0x56 STOP ADDRESS 3
# 0x57 DDS CYCLE 3

# 0x58 START DELAY 2
# 0x59 START ADDRESS 2
# 0x5A STOP ADDRESS 2
# 0x5B DDS CYCLE 2

# 0x5C START DELAY 1
# 0x5D START ADDRESS 1
# 0x5E STOP ADDRESS 1
# 0x5F DDS CYCLE 1

# 0x60 CFG ERROR

# 0x6000 to 0x6FFF SRAM DATA (4096 total samples. Each 12-bit sample occupies the top 12 MSBs of the 16-bit register, the 4 LSbs are reserved.)
