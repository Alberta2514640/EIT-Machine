import time
import usb_cdc
import digitalio
import board
# documentation https://docs.circuitpython.org/en/latest/shared-bindings/usb_cdc/index.html

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

while True:
    # Check if data is available
    if usb_cdc.data.in_waiting>0:
        # Read data from the USB CDC interface
        indata = usb_cdc.data.readline()  # Read up to 64 bytes of data
        if indata:
            print("Received:", indata)
            led.value = True
            time.sleep(0.1)
            led.value = False
            usb_cdc.data.write(b"Hello from Pico!\n")
        # Process received data here
    #usb_cdc.console.send("Hello from Pico!\n")

    #time.sleep(1)
