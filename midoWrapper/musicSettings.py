from .musicType import *


class MusicSettings:
    def __init__(self):
        self.KEY: Key_T = "C"
        self.BPM = 120  # Beats per minute
        self.VELOCITY = 64  # MIDI note velocity

        # The rhythm of the generated music
        self.TICK_PER_BEAT = 480  # Tick per beat
        self.NUMERATOR = 4
        self.DENOMINATOR = 4  # 4/4

    @property
    def BAR_LENGTH(self):
        return self.NUMERATOR * self.TICK_PER_BEAT

    @property
    def QUARTER(self):
        return self.BAR_LENGTH // self.DENOMINATOR

    @property
    def WHOLE(self):
        return self.BAR_LENGTH

    @property
    def HALF(self):
        return self.QUARTER * 2

    @property
    def EIGHTH(self):
        return self.QUARTER // 2

    @property
    def SIXTEENTH(self):
        return self.QUARTER // 4

    @property
    def NOTE_LENGTH(self):
        return [self.HALF, self.QUARTER, self.EIGHTH]

    @property
    def NOTE_UNIT(self):
        return min(self.NOTE_LENGTH)
