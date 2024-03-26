# User SPI Wrapper
# Manages locks for more complicated SPI operations, since it appears that
# CircuitPython SPI register support isn't ready yet as of CircuitPython 9.0.0.

import time
import busio
import digitalio

# Try locking the SPI up to 10 times. Returns true if lock acquired, and false if lock cannot be acquired.
def user_try_lock (spi:busio.SPI, cs: digitalio.DigitalInOut):
    print ("Hello World!")
    for i in range(10):
        if spi.try_lock():
            print("SPI Lock acquired")
            if cs != None:
                cs.value = False
            return True
        time.sleep(0.1)
    print ("SPI Lock ", spi, " could not be acquired")
    return False

def user_unlock (spi:busio.SPI, cs: digitalio.DigitalInOut):
    spi.unlock()
    if cs != None:
        cs.value = True
    print("SPI Lock released")

# Wrapper for writing to SPI devices, lock managed
def write (spi:busio.SPI, chip_select:digitalio.DigitalInOut, bytes_to_write:int, inputbuffer:bytearray):
    if user_try_lock(spi, chip_select) == False:
        print ("SPI write failed")
        return 1
    spi.write(inputbuffer, start=0, end=bytes_to_write)
    user_unlock(spi, chip_select)
    return 0

# Wrapper for reading from SPI devices, lock managed. We only really need this for the AD7680, but it's also useful for debugging.
def read (spi:busio.SPI, chip_select:digitalio.DigitalInOut, bytes_to_read:int, outputbuffer:bytearray):
    if user_try_lock(spi, chip_select) == False:
        print ("SPI read failed.")
        return 1
    test_buffer = bytearray(bytes_to_read)
    spi.readinto(test_buffer, start=0, end=bytes_to_read)
    user_unlock(spi, chip_select)
    return 0

# Wrapper for writing to SPI registers, lock managed. First writes a register address with write bit (command word), then the data.
# We only need to worry about 16-bit command words, but we do have variable register lengths. Some of the registers are two words long.
# The command bit is the MSB (15) of the 16-bit command word. 0 for write.
def reg_write (spi:busio.SPI, chip_select:digitalio.DigitalInOut, register_addr:bytearray, bytes_to_write:int, inbuffer:bytearray):
    command_word = bytearray(len(register_addr))
    command_word[15] = 0
    write (spi, chip_select, bytes_to_write, inbuffer)
    pass

# Wrapper for reading from SPI registers, lock managed. First writes a register address with read bit (command word), then reads the data.
# The command bit is the MSB (15) of the 16-bit command word. 1 for read.
def reg_read (spi:busio.SPI, chip_select:digitalio.DigitalInOut, register_addr:bytearray, bytes_to_read:int, outbuffer:bytearray):
    command_word = bytearray(len(register_addr))
    command_word[15] = 1
    read (spi, chip_select, bytes_to_read, outbuffer)
    pass
