import time
import board
import digitalio
import supervisor
from ledTask import toggle_leds,setup_leds
from AD5391Task import AD5391
# Set up the GPIO pins for the LEDs


setup_leds()

# Initialize AD5391
dac = AD5391()

def process_command(command):
    if command == "info":
        response = "This is a Basic 16 Channel Arbitrary Waveform Generator v0.01"
    else:
        response = "Unknown command"
    return response



next_toggle = time.monotonic() + 1

while True:
    now = time.monotonic()
    if now >= next_toggle:
        toggle_leds()
        next_toggle = now + 0.1

    if supervisor.runtime.serial_bytes_available:
        command = input().strip()
        response = process_command(command)
        print(response)
