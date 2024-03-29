# Functions for interacting with Analog Devices AD9512 clock buffer ICs.

import digitalio

# Startup procedure (We don't need to mess with this thing after init)
def init(ad9512_cs:digitalio.DigitalInOut):
    # Power down unused CLK outputs (1,2,3) since they are not populated on prototype board
    # Power down unused CLK2 input (0x45 <2>)
    # Bypass all dividers
    # Update registers
    pass

# Serial control format:
# All SPI transactions on the AD9512 are preceded by a 16-bit control word written to it by the primary.
# 15: Read/Write Bit (0 Write, 1 Read) | 14-13: Read/Write Length Crumb | 12-0: 13-Bit Register Base Address
# If bits 14-13 == 0b11, then writes will be in streaming mode, Reads will be 4 bytes in length.
# In streaming mode, register address automatically increments (MSB first) or decrements (LSB first).
# Note that register base address bits 12-7 MUST BE zero, as the register address space only occupies up to 0x5A, 0b0101 1010.
# For register changes to take effect, the update bit (0) in the update register (0x5A) must be set. This bit is self clearing.

# Register Map

# 0x00 Serial Control Port Configuration (Leave at default)

## Fine Delay Adjust (Won't be using these)
# 0x34 Delay Bypass 4
# 0x35 Delay Full-Scale 4
# 0x36 Delay Fine Adjust 4

## Outputs
# 0x3D LVPECL OUT 0 (Power up for DDS1)
# 0x3E LVPECL OUT 1 (Power down)
# 0x3F LVPECL OUT 2 (Power down)
# 0x40 LVDS_SMOS OUT 3 (Power down)
# 0x41 LVDS_CMOS OUT 4 (Remain powered up for debug)

## CLK1 AND CLK2
# 0x45 Clocks Select, Power-Down Options (Power down CLK2)

## Dividers (Set to bypass)
# 0x4A Divider 0 Config 1
# 0x4B Divider 0 Config 2
# 0x4C Divider 1 Config 1
# 0x4D Divider 1 Config 2
# 0x4E Divider 2 Config 1
# 0x4F Divider 2 Config 2
# 0x50 Divider 3 Config 1
# 0x51 Divider 3 Config 2
# 0x52 Divider 4 Config 1
# 0x53 Divider 4 Config 2

## FUNCTION
# 0x58 FUNCTION Pin and Sync (Leave at default)
# 0x5A Update Registers (Make sure to write to this after writing to registers, to update their effects.)
