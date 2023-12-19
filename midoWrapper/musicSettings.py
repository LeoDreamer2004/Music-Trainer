from .musicType import *


class MusicSettings:
    def __init__(self):
        self.key: Key_T = "C"
        self.bpm = 120  # Beats per minute
        self.velocity = 64  # MIDI note velocity

        # The rhythm of the generated music
        self.tick_per_beat = 480  # Tick per beat
        self.numerator = 4
        self.denominator = 4  # 4/4

    @property
    def bar_length(self):
        return self.numerator * self.tick_per_beat

    @property
    def quarter(self):
        return self.bar_length // self.denominator

    @property
    def whole(self):
        return self.bar_length

    @property
    def half(self):
        return self.quarter * 2

    @property
    def eighth(self):
        return self.quarter // 2

    @property
    def sixteenth(self):
        return self.quarter // 4

    @property
    def note_length(self):
        return [self.half, self.quarter, self.eighth]

    @property
    def note_unit(self):
        return min(self.note_length)
