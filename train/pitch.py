from copy import deepcopy
from random import choice, randint, random
import numpy as np
from .base import *

DEBUG = True
# the weight for mean, standard deviation of intervals
p1, p2 = 2, 2
# the weight for bad notes (outside the mode)
p3 = 5
# the weight for three notes
p4 = 1
# the weight for emotion
p5 = 3
# coefficient for similarity
mean_coeff = np.array([2, 1, 1, 1, 1, 1, 1, 2])
standard_coeff = np.array([1, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 1])
emotion_coeff = np.array(
    [1.5, 0.5, 0.8, 1, 1.5, 0.5, 0.8, 2, 1.5, 0.5, 0.8, 1, 1.5, 0.5, 0.8, 3]
)
interval_emotion_dict = {
    1: 1,  # unison: tonic, stable & cadence
    2: 4,  # second: supertonic, tension
    3: 3,  # third: mediant, semi-stable
    4: 5,  # fourth: subdominant, strong tension
    5: 4,  # fifth: dominant, tension
    6: 2,  # sixth: submediant, semi-cadence
    7: 5,  # seventh: lead, strong tension
}
# the target value
pitch_target = 6
# whether to use three_note_fitness
three_note_fitness = True
# rate of three types of mutation
mutation_rate_1 = 2
mutation_rate_2 = 1
mutation_rate_3 = 1
mutation_rate_4 = 2


class PitchParameter(TrackParameterBase):
    def __init__(self, track: Track) -> None:
        super().__init__(track)
        self.means = np.zeros(self.bar_number, dtype=float)
        self.standard = np.zeros(self.bar_number, dtype=float)
        self.emotion = np.zeros(self.bar_number * 2, dtype=float)
        self.bad_notes = 0
        self.three_notes = 0.0
        self.update_parameters()

    def update_parameters(self):
        self._update_interval_parameters()
        self._update_bad_notes()
        if three_note_fitness:
            self._update_three_note_parameters()
        self._update_emotions()

    def _update_interval_parameters(self):
        for idx, bar in enumerate(self.bars):
            values = []
            for i in range(len(bar) - 1):
                interval = bar[i + 1].pitch - bar[i].pitch
                values.append(abs(interval) / 3)
            if idx > 0:
                # add the interval between the last note of the previous bar
                # and the first note of the current bar
                interval = bar[0].pitch - self.bars[idx - 1][-1].pitch
                values.append(abs(interval) / 3)

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
                if abs(diff1) <= 5 and abs(diff2) <= 5 and diff1 * diff2 >= 0:
                    score_in_bar += 1
                elif diff1 * diff2 < -20:
                    score_in_bar -= 1
            if len(bar) > 2:
                self.three_notes += score_in_bar / (len(bar) - 2)

    def _update_bad_notes(self):
        self.bad_notes = 0
        for note in self.track.note:
            if not Note.in_mode(note.pitch, self.track.key):
                self.bad_notes += 1

    def _update_emotions(self):
        self.emotion = np.zeros(self.bar_number * 2, dtype=float)
        for note in self.track.note:
            if note.start_time % HALF == 0:
                order = Note.ord_in_mode(note.pitch, self.track.key)
                self.emotion[note.start_time // HALF] = interval_emotion_dict[order]
        for i in range(self.bar_number * 2):
            if self.emotion[i] == 0:
                self.emotion[i] = 3  # default emotion


class GAForPitch(TrackGABase):
    def __init__(
        self, reference_track: Track, population: List[Track], mutation_rate: float
    ):
        super().__init__(population, mutation_rate)
        self.ref_param = PitchParameter(reference_track)
        self.has_three_note_fitness = three_note_fitness
        self.update_fitness()

    def get_fitness(self, track: Track) -> float:
        param = PitchParameter(track)
        mean_diff = np.abs(param.means - self.ref_param.means)
        f1 = p1 * np.exp(-(np.dot(mean_coeff, mean_diff) / self.bar_number))
        standard_diff = np.abs(param.standard - self.ref_param.standard)
        f2 = p2 * np.exp(-(np.dot(standard_coeff, standard_diff) / self.bar_number))
        if three_note_fitness:
            f3 = p4 * param.three_notes / self.bar_number
        else:
            f3 = 0
        emotion_diff = np.abs(param.emotion - self.ref_param.emotion)
        f4 = p5 * np.exp(-(np.dot(emotion_coeff, emotion_diff) / (self.bar_number * 2)))

        if DEBUG and random() < 0.01:
            print(f"{f1} \t {f2} \t {f3} \t {f4}")

        return f1 + f2 + f3 + f4

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
            mutate_type = choice_with_weight(
                [self._mutate_1, self._mutate_2, self._mutate_3, self._mutate_4],
                [
                    mutation_rate_1,
                    mutation_rate_2,
                    mutation_rate_3,
                    mutation_rate_4,
                ],
            )
            mutate_type(track)
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

    @staticmethod
    def _mutate_4(track: Track):
        # if a short note has a big interval with the next note, change it
        for idx, note in enumerate(track.note[:-1]):
            if note.length == EIGHTH:
                next_pitch = track.note[idx + 1].pitch
                if abs(note.pitch - next_pitch) > 7:
                    note.pitch = Note.random_pitch_in_mode(
                        track.key, next_pitch - 7, next_pitch + 7
                    )

    def run(self, generation: int):
        best_track = deepcopy(self.population[self.best_index])
        best_fitness = 0
        for i in range(generation):
            if i % 30 == 0:
                print(f"Pitch generation {i}:", end=" ")
                self.show_info()
            self.epoch()
            if self.fitness[self.best_index] > pitch_target:
                print(f"[!] Target reached at generation {i}")
                print(f"final fitness for pitch: {self.fitness[self.best_index]}")
                return self.population[self.best_index]
            elif self.fitness[self.best_index] > best_fitness:
                best_fitness = self.fitness[self.best_index]
                best_track = deepcopy(self.population[self.best_index])

        print(f"[!] Target not reached after {generation} generations")
        print(f"final fitness for pitch: {best_fitness}")
        return best_track
