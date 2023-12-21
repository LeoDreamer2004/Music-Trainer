from copy import deepcopy
from random import choice, randint, random
import numpy as np
from .base import *

# TODO: Fix bugs on _pitch_similarity_of_bars

DEBUG = False
# the weight for mean, standard deviation of intervals
p1 = 3
# the weight for three notes
p2 = 2
# the weight for emotion
p3 = 3
# the weight for echo
p4 = 1
# the weight for melody line
p5 = 2

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
pitch_target = 8.5

# rate of three types of mutation
mutation_rate_1 = 2
mutation_rate_2 = 1
mutation_rate_3 = 1
mutation_rate_4 = 2


class PitchParameter(TrackParameterBase):
    def __init__(self, track: Track) -> None:
        super().__init__(track)
        self.means = np.zeros(self.bar_number, dtype=float)
        self.emotion = np.zeros(self.bar_number * 2, dtype=float)
        self.melody_line = np.zeros(
            self.bar_number * self.settings.bar_length // self.settings.note_unit,
            dtype=float,
        )
        self.bad_notes = 0
        self.three_notes = 0.0
        self.echo = 0.0
        self.update_parameters()

    def update_parameters(self):
        self._update_interval_parameters()
        self._update_bad_notes()
        self._update_three_note_parameters()
        self._update_emotions()
        self._update_echo()
        self._update_melody_line()

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
                continue
            self.means[idx] = np.mean(values)

    def _update_three_note_parameters(self):
        for bar in self.bars:
            score_in_bar = 0
            for idx in range(len(bar) - 2):
                diff1 = bar[idx + 1].pitch - bar[idx].pitch
                diff2 = bar[idx + 2].pitch - bar[idx + 1].pitch
                if abs(diff1) <= 5 and abs(diff2) <= 5 and diff1 * diff2 >= 0:
                    score_in_bar += 1
                elif diff1 * diff2 < -25:
                    score_in_bar -= 3
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
            if note.start_time % self.settings.half == 0:
                order = Note.ord_in_mode(note.pitch, self.track.key)
                self.emotion[
                    note.start_time // self.settings.half
                ] = interval_emotion_dict[order]
        for i in range(self.bar_number * 2):
            if self.emotion[i] == 0:
                self.emotion[i] = 3  # default emotion

    def _pitch_similarity_of_bars(self, bar1: Bar, bar2: Bar):
        diff1 = np.zeros(self.settings.bar_length // self.settings.note_unit, dtype=int)
        diff2 = np.zeros(self.settings.bar_length // self.settings.note_unit, dtype=int)
        bar1_start = bar1[0].start_time
        bar2_start = bar2[0].start_time
        for idx in range(len(bar1) - 1):
            idx1 = (bar1[idx].start_time - bar1_start) // self.settings.note_unit
            diff1[idx1] = bar1[idx].pitch - bar1[idx + 1].pitch
        for idx in range(len(bar2) - 1):
            idx2 = (bar2[idx].start_time - bar2_start) // self.settings.note_unit
            diff2[idx2] = bar2[idx].pitch - bar2[idx + 1].pitch
        return np.mean(np.abs(diff1 - diff2))

    def _update_echo(self):
        # Bar 0 and 2; 1 and 3; 4 and 6; 5 and 7 are echo, etc.
        # If they have the similar pitch difference, the echo will be higher
        self.echo = 0.0
        for bar in range(0, self.bar_number, 4):
            self.echo += self._pitch_similarity_of_bars(
                self.bars[bar], self.bars[bar + 2]
            )
            self.echo += self._pitch_similarity_of_bars(
                self.bars[bar + 1], self.bars[bar + 3]
            )

    def _update_melody_line(self):
        self.melody_line = np.zeros(
            self.bar_number * self.settings.bar_length // self.settings.note_unit,
            dtype=float,
        )
        for note in self.track.note:
            note_size = note.length // self.settings.note_unit

            # debugger for those notes that are too short
            if note.length < self.settings.note_unit:
                if note.start_time % self.settings.note_unit == 0:
                    note_size = 1
                else:
                    continue

            start_idx = note.start_time // self.settings.note_unit
            # fill the melody line with the pitch of the note
            self.melody_line[start_idx : start_idx + note_size] = note.pitch
        self.melody_line -= np.mean(self.melody_line)  # normalize


class GAForPitch(TrackGABase):
    def __init__(
        self,
        reference_track: Track,
        population: List[Track],
        mutation_rate: float,
    ):
        super().__init__(population, mutation_rate)
        self.ref_param = PitchParameter(reference_track)
        self.mean_coeff = np.ones(self.bar_number, dtype=float)
        self.emotion_coeff = np.zeros(self.bar_number * 2, dtype=float)
        self._update_coeff()
        self.update_fitness()

    def _update_coeff(self):
        for idx in range(self.bar_number * 2):
            if idx == self.bar_number * 2 - 1:  # the end of the song
                self.emotion_coeff[idx] = 3
            elif idx % 8 == 7:  # the end of a phrase
                self.emotion_coeff[idx] = 2
            elif idx % 2 == 0 or idx % 8 == 3:  # strong beats
                self.emotion_coeff[idx] = 1
            else:
                self.emotion_coeff[idx] = 0.5
        self.mean_coeff[0] = self.mean_coeff[-1] = 2

    def get_fitness(self, track: Track) -> float:
        param = PitchParameter(track)
        mean_diff = np.abs(param.means - self.ref_param.means)
        f1 = p1 * np.exp(-(np.sum(mean_diff) / self.bar_number))
        f2 = p2 * param.three_notes / self.bar_number
        emotion_diff = np.abs(param.emotion - self.ref_param.emotion)
        f3 = p3 * np.exp(
            -(np.dot(self.emotion_coeff, emotion_diff) / (self.bar_number * 2))
        )
        f4 = p4 * self.bar_number / (param.echo + 1)
        f5 = p5 * np.corrcoef(param.melody_line, self.ref_param.melody_line)[0, 1]

        if DEBUG and random() < 0.01:
            print(f"{f1} \t {f2} \t {f3} \t {f4} \t {f5}")

        return f1 + f2 + f3 + f4 + f5

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

    def _mutate_1(self, track: Track):
        # If the interval between two notes is too large, change it
        for idx in range(len(track.note) - 1):
            if track.note[idx + 1].pitch - track.note[idx].pitch > 12:
                track.note[idx].pitch += 12
            elif track.note[idx + 1].pitch - track.note[idx].pitch < -12:
                track.note[idx].pitch -= 12

    def _mutate_2(self, track: Track):
        # Change the pitch of a random note
        idx = randint(0, len(track.note) - 2)
        track.note[idx].pitch = Note.random_pitch_in_mode(track.key)

    def _mutate_3(self, track: Track):
        # Swap two notes' pitch
        idx = randint(1, len(track.note) - 2)
        track.note[idx], track.note[idx - 1] = track.note[idx - 1], track.note[idx]

    def _mutate_4(self, track: Track):
        # if a short note has a big interval with the next note, change it
        for idx, note in enumerate(track.note[:-1]):
            if note.length <= self.settings.eighth:
                next_pitch = track.note[idx + 1].pitch
                if abs(note.pitch - next_pitch) > 7:
                    note.pitch = Note.random_pitch_in_mode(
                        track.key, next_pitch - 7, next_pitch + 7
                    )
                    return

    def run(self, generation: int):
        best_track = deepcopy(self.population[self.best_index])
        best_fitness = 0

        print("--------- Start Pitch Training ---------")
        succeed = False
        for i in range(generation):
            if i % 30 == 0:
                print(f"Pitch generation {i}: " + self.train_info())
            self.epoch()
            if self.fitness[self.best_index] > pitch_target:
                print(f"[!] Target reached at generation {i}")
                succeed = True
                break
            elif self.fitness[self.best_index] > best_fitness:
                best_fitness = self.fitness[self.best_index]
                best_track = deepcopy(self.population[self.best_index])
        if not succeed:
            print(f"[!] Target not reached after {generation} generations")

        print(f"Final fitness for pitch: {best_fitness}")
        print("--------- Finish Pitch Training ---------")
        return best_track
