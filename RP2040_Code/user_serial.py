# User Serial Wrapper
# Handles for functions that are triggered from SPI devices

import random
import time
import usb_cdc

def update_awg (data_len):
    data = usb_cdc.data.read(data_len)
    formatted = bytearray(data_len)
    # Received data is in
    for i in range(0, data_len, 2):
        # Put the data in the proper form for work
        # Reverse the order to account for endianness
        formatted[i] = data[i + 1]
        formatted[i+1] = data[i]
        temp = data[i+1] << 12 | data[i] << 4
        print (temp)
        print (temp >> 4)
    # Call an AD9106 function to write this into SRAM
    print ("Done reading")
    pass

# Main EIT function

# IMPORTANT! The board requires a physical switch to be togged to switch between EIT and AWG mode.
# This was the result of a design oversight.
# Start to generate 50 kHz sine on HDR1 and prompt user to flip EIT switch.
    # This will be handled by the host computer, so we don't have to worry about it here.
def start_eit():
    # global lEIT_PD, lAMP_PD
    # Configures the amps and DDSes for EIT mode.
    # lEIT_PD.value = True
    # lAMP_PD.value = False
    ext_n = usb_cdc.data.read(1)
    mea_n = usb_cdc.data.read(1)
    # We need to read 2x the number of excitations because they come in pairs
    ext =   usb_cdc.data.read(int.from_bytes(ext_n, 'little') * 2)
    mea = usb_cdc.data.read(int.from_bytes(mea_n, 'little') * 2)
    # print (ext_n)
    # print (ext)
    # print (mea_n)
    # print (mea)
    for i in range (0, 416):
        rand_byte = bytearray(1)
        rand_byte[0] = random.randint(0,255)
        usb_cdc.data.write(rand_byte)
        # time.sleep(0.01)
    # Parses the list of pairs for generation and measurement.
    # ^ This comes from the pyEIT protocol object. Alternatively, we can just hardcode them here.
    # Set up an object that will hold all the measured values in order.
    # while usb_cdc.data.in_waiting == 0:
            # Loop through the generation pairs
            # Configure the current source and sink muxes
            # Loop through the associated measurement pairs
                # Configure the measurement positive and negative muxes
                # Wait for the system to settle
                # Do a one-shot conversion with the AD7680
                # Save the result to the buffer
        # Send the buffer back to the host over USB CDC.
    pass
