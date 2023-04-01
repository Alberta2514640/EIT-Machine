import time

class SquareWaveGenerator:
    def __init__(self, channel, period, amplitude, dac=None):
        self.channel = channel
        self.period = period
        self.amplitude = amplitude
        self.dac = dac if dac is not None else AD5391()
        self.start_time = time.monotonic()

    def progress(self):
        elapsed_time = time.monotonic() - self.start_time
        phase = (elapsed_time % self.period) / self.period
        value = self.amplitude if phase < 0.5 else 0
        self.dac.write_dac(self.channel, value)
