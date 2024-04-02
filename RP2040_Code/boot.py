# Runs before each boot!
# We want to enable the console for debugging and sending commands, and the data port for sending EIT data.

import usb_cdc

usb_cdc.enable(console = True, data = True)
usb_cdc.data.timeout = 0