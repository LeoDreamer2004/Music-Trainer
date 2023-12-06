import numpy as np

########################
# PARAMETERS FOR PITCH #
########################

### Basic parameters for the music ###
reference_file = "reference.mid"
output_file = "result.mid"
bar_number = 8
key_mode = "Db"
with_accompaniment = False

# ----------------------------------------------------
# Parameters for the genetic algorithm
# ----------------------------------------------------

mutation_rate = 0.2
iteration_num = 5000
population_size = 10

# ----------------------------------------------------
# Parameters for the fitness function of pitch
# ----------------------------------------------------

# interval -> value, 0 fot unison, 12 for octave
# bad interval would be given higher value

interval_value_dict = {
    0: 1,
    1: 2,
    2: 2,
    3: 2,
    4: 2,
    5: 1,
    6: 3,
    7: 1,
    8: 3,
    9: 3,
    10: 4,
    11: 4,
    12: 3,
}
# if interval > 12, the value will be 'large_interval_value'

large_interval_value = 5
# the weight for mean, standard deviation of intervals
alpha, beta, delta = 1, 4, 0.1
# the weight for bad notes (outside the mode)
gamma = 0.5
mean_coeff = np.array([2, 1, 1, 1, 1, 1, 1, 2])
standard_coeff = np.array([1, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 1])
# the target value
pitch_target = 2.5

# rate of three types of mutation
mutation_rate_1: int = 2
mutation_rate_2: int = 1
mutation_rate_3: int = 1

# whether to use three_note_fitness
three_note_fitness = True
