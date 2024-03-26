# Functions for interacting with Analog Devices AD9512 clock buffer ICs.

import time

# Startup procedure (We don't need to mess with this thing after init)
def init():
    time.sleep(1)

# Register Map

# 0x00 Serial Control Port Configuration

## Fine Delay Adjust
# 0x34 Delay Bypass 4
# 0x35 Delay Full-Scale 4
# 0x36 Delay Fine Adjust 4

## Outputs
# 0x3D LVPECL OUT 0
# 0x3E LVPECL OUT 1
# 0x3F LVPECL OUT 2
# 0x40 LVDS_SMOS OUT 3
# 0x41 LVDS_CMOS OUT 4

## CLK1 AND CLK2
# 0x45 Clocks Select, Power-Down Options

## Dividers
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
# 0x58 FUNCTION Pin and Sync
# 0x5A Update Registers
