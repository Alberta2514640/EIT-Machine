# Functions for interacting with Analog Devices AD7680 analog to digital converters.

# Function that does a one-shot 24-bit (3 8-bit word) conversion, discards the 4 leading and 4 trailing bits.
# The raw value is sent to the host in the form of a raw 16-bit word. The host will convert it to a floating-point number
# since the RP2040 doesn't have a dedicated FPU.
# Hopefully, this could mean that we can have really fast reconstructions, approaching real-time.
