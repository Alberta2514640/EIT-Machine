import time
import math

class SineWaveGenerator:
    def __init__(self, channel, period, amplitude, dac=None):
        self.channel = channel
        self.period = period
        self.amplitude = amplitude
        self.dac = dac if dac is not None else AD5391()
        self.start_time = time.monotonic()

    def progress(self):
        elapsed_time = time.monotonic() - self.start_time
        phase = (elapsed_time % self.period) / self.period
        value = int(self.amplitude * (1 + math.sin(2 * math.pi * phase)) / 2)
        self.dac.write_dac(self.channel, value)
