from midoWrapper import *
from .pitch import GAForPitch
from .rhythm import GAForRhythm


def train(
    ref_track: Track, population_size: int, mutation_rate: float, iteration_num: int
):
    """Train with GA using a reference track."""
    population = [
        Track(ref_track.sts).generate_random_track() for _ in range(population_size)
    ]
    ga_rhythm = GAForRhythm(population, mutation_rate)
    rhythm_track = ga_rhythm.run(iteration_num)

    # Use the rhythm of the track forever
    population_with_rhythm = [
        Track(ref_track.sts).generate_random_pitch_on_rhythm(rhythm_track)
        for _ in range(population_size)
    ]
    ga_pitch = GAForPitch(ref_track, population_with_rhythm, mutation_rate)
    result = ga_pitch.run(iteration_num)
    return result
