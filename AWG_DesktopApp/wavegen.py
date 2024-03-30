# wavegen.py

from enum import Enum
import serial as ser
import numpy as np
import scipy.signal as sig

# Wave generation for the AD9106. Hoping that continuous waveform generation means that we
# can actually make arbitrary waves. The datasheet is not very clear about this.

# Initialize all the basic variables that we'll need for all of the different waves
# The DDS will be clocked with a 12.5 MHz signal from the PIO, and there will be 1024 samples allocated per waveform.
# The amplitude of the wave can be adjusted by using the gain registers on the AD9106

# Greater resolution could be achieved by using a faster clock (the chip supports up to 180 MHz), using the entire SRAM space (4096 samples)
# or in the case of sine waves, using the DDS output itself. The downside to the latter is that the DDS is shared between all DACs.

# Function that generates and returns the array of integers to be sent, along with the time base (for plotting)
# The graph will vary between -1 and 1, since the amplitudes are expected to be applied by other functions.
def gen_graph (freq, phase, type:str):
    time_slice = 1 / (12.5e6) # 12.5 MHz DDS base clock
    phase_offset = np.deg2rad(phase) / (2 * np.pi * freq)
    time = np.empty(1024)
    theta = np.empty(1024)
    for i in range(0, 1024):
        time[i] = i * time_slice
        theta[i] = (2 * np.pi * freq) * (time[i] + phase_offset) # sin(2*pi*f*(t + phi))
    # Note that this match syntax only works in Python versions 3.10.0 and above.
    match type.upper():
        # Must be in integer form to transfer to the DDS SRAM
        case "SINE":
            wave = np.sin(theta)
        case "COSINE":
            wave = np.cos(theta)
        case "SQUARE":
            wave = sig.square (theta, duty=0.5)
        case "TRIANGLE":
            # The AD9106 actually has a built-in sawtooth generator that can generate ramp up, ramp down, and triangle waves.
            # However, to ease the burden of dealing with those registers, we will just generate those waves here in Python,
            # using the same pipeline we are using to generate other arbitrary waves.
            wave = sig.sawtooth (theta, width=0.5)
        case "SAW UP":
            wave = sig.sawtooth (theta, width=1)
        case "SAW DOWN":
            wave = sig.sawtooth (theta, width=0)
    return time, wave

# Wrapper that handles generating the wave based on the given WaveType enum.
# Handles sending the wave to the device over the given COM port.
# Returns a fig, ax pair that can be used to plot the generated waveform through matplotlib integration in PySimpleGUI.
def generate_and_send(amplitude, frequency, phase, channel:int, type:str, ser_port:ser.Serial):
    time, data = gen_graph (frequency, phase, type)
    # Put the data into an array of bytes
    # Set the limit to max and then round.
    bit_depth = 12
    max = (np.power(2, bit_depth-1) - 1) # Maximum value based on bit depth (n-bit signed int)
    data *= max
    data = np.rint(data)
    data = data.astype(np.int16)
    print (data)
    data_bytes = bytearray(0)
    for i in range (0, 1024):
        data_bytes.append(data[i] & 0x00FF)
        data_bytes.append((data[i] & 0xFF00) >> 8)
    return time, data


# Function that sends formatted SRAM data to the device over the COM port.
# The device on the other end is responsible for chopping off the top 4 MSBs.
def send_ser(amplitude, channel, data:bytearray, ser_port:ser.Serial):
    # Send instruction to start listening for bulk SRAM data transfer intended for a certain channel
    # Perform the bulk transfer
    # Wait for a certain amount of time for the device to acknowledge receipt
    pass