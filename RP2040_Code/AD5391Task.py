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

#   Write a Value to the DAC (24 bit data word)
#   24 bits are as follows
#   ~A/B, R/~W, 0, 0, A3, A2, A1, A0, REG1, REG0, DB11, DB10, DB9, DB8, DB7, DB6, DB5, DB4, DB3, DB2, DB1, DB0, X, X
#   23  ,22   , 21,20,19, 18, 17, 16, 15,   14 
#   ~A/B Toggle Mode, Determines if data is written to the A or B Register
#   R/~W Read Write Control Bit
#   A3- A0 Addresses the Input Channels
#   REG 1 and REG 0 Which Register is Written to
#   DB11 - DB0 Data being Written (Last 2 bits are don't cares because they are for other chips which are good to 14 bits. )
    def write_dac(self, channel, value, toggle_mode=False, ab_select=False, reg_select=3):
        # Asserts that the Channel Must be Between 0 and 15. Given this is a 16 channel DAC
        assert 0 <= channel <= 15, "Channel must be between 0 and 15"
        # Asserts that the output value must be between 0 and 4095 
        assert 0 <= value <= 4095, "Value must be between 0 and 4095"
        # Asserts that the register must be between 0 and 3 this must be given the values. 
        # 3 input data Register (Defaults to this Register)
        # 2 Offset Register 
        # 1 Gain Register
        # 0 Special Function Register
        assert 0 <= reg_select <= 3, "Register select must be between 0 and 3"

        ab_bit = 1 if toggle_mode and ab_select else 0
        rw_bit = 0  # Write operation
        address = (channel & 0b1111)
        reg_bits = (reg_select & 0b11)

        control_bits = ab_bit << 23 | rw_bit << 22 | address << 16 | reg_bits << 14
        data_bits = (value & 0xFFF) << 2
        spi_data = (control_bits | data_bits).to_bytes(3, "big")

        self.spi.try_lock()
        self.SYNC.value = False
        self.spi.write(spi_data)
        self.SYNC.value = True
        self.spi.unlock()

# Write DAC RAW Function (To Try and Activate the Internal Reference by setting the control register)
# Writing Control Register
# REG1=REG0=0
# A3-A0 = 1100
# DB13-DB0 Contains CR13 - CR0
# This Setup gives the following
# A/~B = 0
# R/~W = 0
# 00 (Always 0)
# A3-A0 = 1100 (Control Register)
# REG1-REG0 = 00 (Special Functions)
# DB13 - DB12 = Doesn't apply to AD5391
# CR11 = 1 Power Down Status. Configures the Amplifier Behavior in Power Down
# CR10 = 0 REF Select (Sets the Internal Reference 1/2,5V 0/1.25V)
# CR9 = 1 Current Boost Control (1 Maximizes the bias current to the output amplifier while in increasing power consumption)
# CR8 = 1 Internal / External Reference (1 Uses Internal Reference)
# CR7 = 1 Enable Channel Monitor Function (1 allows channels to be routed to the output)
# CR6 = 0 Enable Thermal Monitor Function 
# CR5-CR2 = Don't CARE
# CR3-CR2 = Toggle Function Enable 
    def write_dac_raw(self, data):
        assert isinstance(data, int) and data >= 0 and data < (1 << 24), "Data must be a 24-bit integer"
        
        self.spi.try_lock()
        self.SYNC.value = False
        self.spi.write(data.to_bytes(3, "big"))
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
