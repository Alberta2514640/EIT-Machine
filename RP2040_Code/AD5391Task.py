# ad5391.py
import board
import digitalio
import busio

class AD5391:
    def __init__(self):
        self.RESET = digitalio.DigitalInOut(board.GP14)
        self.RESET.direction = digitalio.Direction.OUTPUT
        self.RESET.value = False  # Set the reset pin low (active low)

 
        self.SYNC = digitalio.DigitalInOut(board.GP10)
        self.SYNC.direction = digitalio.Direction.OUTPUT

        self.PD = digitalio.DigitalInOut(board.GP15)
        self.PD.direction = digitalio.Direction.OUTPUT

        self.LDAC = digitalio.DigitalInOut(board.GP22)
        self.LDAC.direction = digitalio.Direction.OUTPUT


        self.CLR = digitalio.DigitalInOut(board.GP21)
        self.CLR.direction = digitalio.Direction.OUTPUT

        self.BUSY = digitalio.DigitalInOut(board.GP20)
        self.BUSY.direction = digitalio.Direction.INPUT

        self.MON_OUT = digitalio.DigitalInOut(board.GP26)
        self.MON_OUT.direction = digitalio.Direction.INPUT

        self.RESET.value = False  # Set the reset pin high (active low)

        # SPI setup
        #self.spi = busio.SPI(SCK=board.GP18, MISO=board.GP16, MOSI=board.GP19)
        # while not self.spi.try_lock():
        #     pass
        # self.spi.configure(baudrate=50000000)  # Set SPI clock speed to 50 MHz
        # self.spi.unlock()

