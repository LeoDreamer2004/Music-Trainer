import numpy as np

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

# interval -> value
# 0 fot unison, 12 for octave
# if interval > 12, the value will be 'large_interval_value'
interval_value_dict = {
    0: 3, 1: 2, 2: 2, 3: 2, 4: 2, 5: 1, 6: 3, 7: 3, 8: 4, 9: 4, 10: 5, 11: 5, 12: 5
}
large_interval_value = 5

alpha, beta, gamma, delta = 1, 1, 0.5, 0.03
mean_coeff = np.array([2, 1, 1, 1, 1, 1, 1, 2])
standard_coeff = np.array([1, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 1])
target = 1.5

three_note_fitness = True
verbose = True

# rate of three types of mutation
mutation_rate_1: int = 3
mutation_rate_2: int = 2
mutation_rate_3: int = 1

mutation_rate = 0.5
