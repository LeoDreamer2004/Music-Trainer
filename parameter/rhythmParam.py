# the weight for strong beats
theta = 0.5
# the weight for echo
delta = 1
# pass
epsilon = 0.3
# the punishment for long notes
omiga = 0.1
# the punishment for neighboring notes with large length gap
omicron = 0.1
# the target value
rhythm_target = 3.5

# rate of four types of mutation
mutation_rate_1: int = 1  # Swap two notes' length
mutation_rate_2: int = 5  # Split a note into two notes
mutation_rate_3: int = 1  # Merge two notes into one note
mutation_rate_4: int = 2  # Copy a bar and paste it to another bar
