# Functions that implement the EIT mode of the 16CH_EIT.
# These functions create the list of combinations for generation and measurement, configure the DACs and muxes,
# gather the information from the ADC, and package it to send to the host PC.

# IMPORTANT! The board requires a physical switch to be togged to switch between EIT and AWG mode.
# This was the result of a design oversight.

# Main EIT function
# Configures the amps and DDSes for EIT mode.
# Start to generate 50 kHz sine on HDR1 and prompt user to flip EIT switch.
# Parses the list of pairs for generation and measurement.
  # ^ This comes from the pyEIT protocol object. Alternatively, we can just hardcode them here.
# Set up an object that will hold all the measured values in order.
# (Some kind of way to interrupt infinite loop of EIT mode by USB)
# Loop through the generation pairs
    # Configure the current source and sink muxes
    # Loop through the associated measurement pairs
        # Configure the measurement positive and negative muxes
        # Wait for the system to settle
        # Do a one-shot conversion with the AD7680
        # Save the result to the buffer
# Send the buffer back to the host over USB CDC.
