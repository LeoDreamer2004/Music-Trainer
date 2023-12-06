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
WHOLE = 4 * TICK_PER_BEAT
HALF = 2 * TICK_PER_BEAT
QUARTER = 1 * TICK_PER_BEAT
EIGHTH = QUARTER // 2
SIXTEENTH = QUARTER // 4
NOTE_LENGTH = [HALF, QUARTER, EIGHTH]

BAR_LENGTH = NUMERATOR * TICK_PER_BEAT
