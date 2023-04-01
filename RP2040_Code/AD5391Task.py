# ad5391.py
import board
import digitalio
import busio
import time
import analogio

class AD5391:
    def __init__(self):
        self.RESET = digitalio.DigitalInOut(board.GP14)
        self.RESET.direction = digitalio.Direction.OUTPUT
        self.RESET.value = False  # Set the reset pin low (active low)

        self.RESET.value = True # Set the reset pin high (active low)

        self.SYNC = digitalio.DigitalInOut(board.GP10)
        self.SYNC.direction = digitalio.Direction.OUTPUT
        self.SYNC.value = False

        self.PD = digitalio.DigitalInOut(board.GP15)
        self.PD.direction = digitalio.Direction.OUTPUT
        self.PD.value = False

        self.LDAC = digitalio.DigitalInOut(board.GP22)
        self.LDAC.direction = digitalio.Direction.OUTPUT
        self.LDAC.value = False

        self.CLR = digitalio.DigitalInOut(board.GP21)
        self.CLR.direction = digitalio.Direction.OUTPUT
        self.CLR.value = True


        self.BUSY = digitalio.DigitalInOut(board.GP20)
        self.BUSY.direction = digitalio.Direction.INPUT

        self.MON_OUT = analogio.AnalogIn(board.GP26)


        # SPI setup
        self.spi = busio.SPI(board.GP18, MISO=board.GP16, MOSI=board.GP19)
        while not self.spi.try_lock():
             pass
        self.spi.configure(baudrate=50000000)  # Set SPI clock speed to 50 MHz
        self.spi.unlock()

    #read MON_OUT value
    def read_mon_out(self):
        return self.MON_OUT.value

    #read MON_OUT voltage
    def read_mon_out_voltage(self):
        return self.MON_OUT.value * 3.3 / 65535

    def read_busy_pin(self):
        return self.BUSY.value

    def set_ldac_pin(self, state):
        self.LDAC.value = state

    def write_dac(self, channel, value, toggle_mode=False, ab_select=False, reg_select=0):
        assert 0 <= channel <= 15, "Channel must be between 0 and 15"
        assert 0 <= value <= 4095, "Value must be between 0 and 4095"
        assert 0 <= reg_select <= 3, "Register select must be between 0 and 3"

        ab_bit = 1 if toggle_mode and ab_select else 0
        rw_bit = 0  # Write operation
        address = (channel & 0b1111) << 3
        reg_bits = (reg_select & 0b11) << 1

        control_bits = ab_bit << 23 | rw_bit << 22 | address << 18 | reg_bits << 16
        data_bits = (value & 0xFFF) << 4
        spi_data = (control_bits | data_bits).to_bytes(3, "big")

        self.spi.try_lock()
        self.SYNC.value = False
        self.spi.write(spi_data)
        self.SYNC.value = True
        self.spi.unlock()

    def write_clr_code(self, clr_data):
        command = (0b0001 << 20) | (clr_data & 0x3FFF) << 6
        self.send_sfr_command(command.to_bytes(3, 'big'))

    def soft_clr(self):
        command = 0b0010 << 20
        self.send_sfr_command(command.to_bytes(3, 'big'))

    def soft_power_down(self):
        command = 0b1000 << 20
        self.send_sfr_command(command.to_bytes(3, 'big'))

    def soft_power_up(self):
        command = 0b1001 << 20
        self.send_sfr_command(command.to_bytes(3, 'big'))

    def soft_reset(self):
        command = 0b001111 << 20
        self.send_sfr_command(command.to_bytes(3, 'big'))

    def monitor_channel(self, channel):
        command = (0b01010 << 20) | (channel & 0x3F) << 14
        self.send_sfr_command(command.to_bytes(3, 'big'))


    def send_sfr_command(self, command):
        while not self.spi.try_lock():
            pass

        self.spi.write(command)
        self.spi.unlock()
