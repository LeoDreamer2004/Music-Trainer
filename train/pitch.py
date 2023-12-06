from copy import deepcopy
from random import choice, randint, random
import numpy as np
from .base import *

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
# whether to use three_note_fitness
three_note_fitness = True
# rate of three types of mutation
mutation_rate_1 = 2
mutation_rate_2 = 1
mutation_rate_3 = 1


class PitchParameter(TrackParameterBase):
    """Used to calculate parameters of the tracks"""

    def __init__(self, track: Track) -> None:
        super().__init__(track)
        self.means = np.zeros(self.bar_number, dtype=float)
        self.standard = np.zeros(self.bar_number, dtype=float)
        self.bad_notes = 0
        self.three_note_score = 0  # the score of three notes in a bar
        self.update_parameters()

    @staticmethod
    def _interval_to_value(interval: int):
        # return interval_value_dict.get(abs(interval), large_interval_value)
        return abs(interval) / 3

    def update_parameters(self):
        self._update_interval_parameters()
        self._update_bad_notes()
        if three_note_fitness:
            self._update_three_note_parameters()

    def _update_interval_parameters(self):
        for idx, bar in enumerate(self.bars):
            values = []
            for i in range(len(bar) - 1):
                interval = bar[i + 1].pitch - bar[i].pitch
                values.append(self._interval_to_value(interval))
            if idx > 0:
                # add the interval between the last note of the previous bar
                # and the first note of the current bar
                interval = bar[0].pitch - self.bars[idx - 1][-1].pitch
                values.append(self._interval_to_value(interval))

            if not values:
                self.means[idx] = 0
                self.standard[idx] = 0
                continue

            self.means[idx] = np.mean(values)
            self.standard[idx] = np.std(values)

    def _update_three_note_parameters(self):
        """Calculate the score of three notes in a bar.
        If the pitches of three notes is similar to an arithmetic sequence,
        it has better score.
        The more three notes, the lower the score."""
        for bar in self.bars:
            score_in_bar = 0
            for idx in range(len(bar) - 2):
                diff1 = bar[idx + 1].pitch - bar[idx].pitch
                diff2 = bar[idx + 2].pitch - bar[idx + 1].pitch
                if (
                    abs(diff1 - diff2) <= 2
                    and diff1 * diff2 > 0
                    and (diff1 != 0 or diff2 != 0)
                ):
                    score_in_bar += 1
            self.three_note_score += len(bar) / ((score_in_bar + 1) * 3)

    def _update_bad_notes(self):
        self.bad_notes = 0
        for note in self.track.note:
            if not Note.in_mode(note.pitch, self.track.key):
                self.bad_notes += 1


class GAForPitch(TrackGABase):
    def __init__(
        self, reference_track: Track, population: List[Track], mutation_rate: float
    ):
        super().__init__(population, mutation_rate)
        self.ref_param = PitchParameter(reference_track)
        self.has_three_note_fitness = three_note_fitness
        self.update_fitness()

    def get_fitness(self, track: Track) -> float:
        # It's better to have a lower fitness
        track_param = PitchParameter(track)
        mean_diff = np.abs(track_param.means - self.ref_param.means)
        f1 = alpha * np.dot(mean_coeff, mean_diff)
        standard_diff = np.abs(track_param.standard - self.ref_param.standard)
        f2 = beta * np.dot(standard_coeff, standard_diff)
        g = gamma * track_param.bad_notes

        if three_note_fitness:
            f3 = track_param.three_note_score * delta
        else:
            f3 = 0

        return f1 + f2 + g + f3

    def select(self):
        for i in range(len(self.fitness)):
            if self.fitness[i] < self.fitness[self.best_index]:
                self.best_index = i
                self.second_index = self.best_index
            elif self.fitness[i] < self.fitness[self.second_index]:
                self.second_index = i

    def crossover(self):
        # No crossover for pitch
        pass

    def mutate(self):
        for i in range(len(self.population)):
            if random() > self.mutation_rate:
                continue
            # TODO: mutation
            track = deepcopy(
                self.population[choice([self.best_index, self.second_index])]
            )
            mutate_type = randint(
                1, mutation_rate_1 + mutation_rate_2 + mutation_rate_3
            )
            # When mutating, do not change the last note pitch,
            # because we want the last note to be the tonic
            if mutate_type <= mutation_rate_1:
                self._mutate_1(track)
            elif mutate_type <= mutation_rate_1 + mutation_rate_2:
                self._mutate_2(track)
            else:
                self._mutate_3(track)
            self.population[i] = track

    @staticmethod
    def _mutate_1(track: Track):
        # If the interval between two notes is too large, change it
        for idx in range(len(track.note) - 1):
            if track.note[idx + 1].pitch - track.note[idx].pitch > 12:
                track.note[idx].pitch += 12
            elif track.note[idx + 1].pitch - track.note[idx].pitch < -12:
                track.note[idx].pitch -= 12

    @staticmethod
    def _mutate_2(track: Track):
        # Change the pitch of a random note
        idx = randint(0, len(track.note) - 2)
        track.note[idx].pitch = Note.random_pitch_in_mode(track.key)

    @staticmethod
    def _mutate_3(track: Track):
        # Swap two notes' pitch
        idx = randint(1, len(track.note) - 2)
        track.note[idx], track.note[idx - 1] = track.note[idx - 1], track.note[idx]

    def run(self, generation: int):
        best_track = deepcopy(self.population[self.best_index])
        best_fitness = float("inf")
        for i in range(generation):
            if i % 30 == 0:
                print(f"Pitch generation {i}:", end=" ")
                self.show_info()
            self.epoch()
            if self.fitness[self.best_index] < pitch_target:
                print(f"[!] Target reached at generation {i}")
                print(f"final fitness for pitch: {self.fitness[self.best_index]}")
                return self.population[self.best_index]
            elif self.fitness[self.best_index] < best_fitness:
                best_fitness = self.fitness[self.best_index]
                best_track = deepcopy(self.population[self.best_index])

        print(f"[!] Target not reached after {generation} generations")
        print(f"final fitness for pitch: {best_fitness}")
        return best_track
