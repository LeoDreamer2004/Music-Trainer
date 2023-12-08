BPM = 120  # Beats per minute
VELOCITY = 64  # MIDI note velocity
TICK_PER_BEAT = 480  # Tick per beat

# The rhythm of the generated music
NUMERATOR = 4
DENOMINATOR = 4  # 4/4

# The range of notes to be generated
NOTE_MIN = 60  # C4
NOTE_MAX = 84  # C6

# Note lengths
BAR_LENGTH = NUMERATOR * TICK_PER_BEAT

QUARTER = BAR_LENGTH // DENOMINATOR
WHOLE = BAR_LENGTH
HALF = QUARTER * 2
EIGHTH = QUARTER // 2
SIXTEENTH = QUARTER // 4
NOTE_LENGTH = [HALF, QUARTER, EIGHTH]

NOTE_UNIT = min(NOTE_LENGTH)
