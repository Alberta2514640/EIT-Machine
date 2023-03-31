import board
import digitalio

led_pins = [board.GP1, board.GP2, board.GP3, board.GP4]
leds = []
current_led = 0 # global variable to keep track of the current LED index


def setup_leds():
    for pin in led_pins:
        led = digitalio.DigitalInOut(pin)
        led.direction = digitalio.Direction.OUTPUT
        leds.append(led)

def toggle_leds():
    global current_led # use the global variable
    leds[current_led].value = not leds[current_led].value
    current_led = (current_led + 1) % len(leds) # increment current_led and wrap around if necessary