# User Serial Wrapper
# Handles for functions that are triggered from SPI devices

import time
import random
import busio
import digitalio
import bitbangio
import usb_cdc

import ad7680
import sn74hc595

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
def start_eit(adc_spi:busio.SPI, adc_cs:digitalio.DigitalInOut,
              sr_spi:bitbangio.SPI, sr_oe:digitalio.DigitalInOut, sr_clr:digitalio.DigitalInOut):
    # global lEIT_PD, lAMP_PD
    # Configures the amps and DDSes for EIT mode.
    # lEIT_PD.value = True
    # lAMP_PD.value = False
    ext_n = usb_cdc.data.read(1)
    mea_n = usb_cdc.data.read(1)
    # We need to read 2x the number of excitations because they come in pairs
    ext =   usb_cdc.data.read(int.from_bytes(ext_n, 'little') * 2)
    mea = usb_cdc.data.read(int.from_bytes(mea_n, 'little') * 2)
    print (len(ext))
    print (ext)
    print (len(mea))
    print (mea)
    # Iterate over the excitations
    for i in range (0, 32, 2): # 16 excitation pairs
        # 0 is source, 1 is sink
        ext_src = ext[i]
        ext_snk = ext[i+1]
        print ("Excite node", ext_src, ext_snk)
        for j in range (0, 26, 2): # 13 measurement pairs per excitation
            # 0 is positive, 1 is negative
            mes_pos = mea[j+(i+13)]
            mes_neg = mea[j+(i+13)+1]
            print ("Measure node", mes_pos, mes_neg)
            # Adjust the shift register to point to the right place!
            # sn74hc595.sr_update(sr_spi, sr_clr, sr_oe, ext_src, ext_snk, mes_pos, mes_neg)
            outval = ad7680.single_conv(adc_spi, adc_cs)
            # print (outval)
            out_bytes = outval.to_bytes(2, 'little') # Might wanna keep an eye on this, don't know if it'll end up being big instead
            # print (out_bytes)
            usb_cdc.data.write(out_bytes)
            pass
            # Iterate over the measurements the correspond to t
    for i in range (0, 416): # Send random bytes
        # rand_byte = bytearray(1)
        # rand_byte[0] = random.randint(0,255)
        # usb_cdc.data.write(rand_byte)
        pass
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
