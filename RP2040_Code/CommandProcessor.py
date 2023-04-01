class CommandProcessor:
    def __init__(self,ad5391):
        self.ad5391 = ad5391

    def process_command(self, command):
        if command == "info":
            response = "This is a Basic 16 Channel Arbitrary Waveform Generator v0.01"
        elif command == "read_mon_out":
            mon_out_value = self.ad5391.read_mon_out()
            response = f"MON_OUT value: {mon_out_value}"
        elif command == "read_mon_out_voltage":
            mon_out_voltage = self.ad5391.read_mon_out_voltage()
            response = f"MON_OUT voltage: {mon_out_voltage:.4f} V"
        elif command == "read_busy_pin":
            busy_state = self.ad5391.read_busy_pin()
            response = f"BUSY pin state: {busy_state}"
        else:
            response = "Unknown command"
        return response
