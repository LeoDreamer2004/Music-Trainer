from random import choice, randint, random
from .base import *
from copy import deepcopy

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
mutation_rate_1 = 1  # Swap two notes' length
mutation_rate_2 = 5  # Split a note into two notes
mutation_rate_3 = 1  # Merge two notes into one note
mutation_rate_4 = 2  # Copy a bar and paste it to another bar


class RyhthmParameter(TrackParameterBase):
    def __init__(self, track: Track) -> None:
        super().__init__(track)
        self.strong_beats = 0
        self.echo = 0.0
        self.long_notes = 0.0
        self.neighboring_notes = 0.0
        self.strong_notes_on_weak_beats = 0.0
        self.update_parameters()

    def update_parameters(self):
        self._update_beats()
        self._update_echo()
        self._update_long_notes()
        self._update_neighboring_notes()

    def _update_beats(self):
        self.strong_beats = 0
        self.strong_notes_on_weak_beats = 0
        for bar in self.bars:
            bad_beats = 0
            for note in bar:
                if note.start_time % HALF == 0:
                    self.strong_beats += 1
                # elif note.start_time % QUARTER == 0:
                # self.weak_beats += 1
                elif note.start_time % note.length != 0:
                    bad_beats += 1
            self.strong_notes_on_weak_beats += bad_beats / len(bar)

    def _update_echo(self):
        # Bar 0 and 2; 1 and 3; 4 and 6; 5 and 7 are echo, etc.
        # If they have the similar rhythm, the echo will be higher
        for bar in range(0, self.bar_number, 4):
            self.echo += self._rhythm_similarity_of_bars(
                self.bars[bar], self.bars[bar + 2]
            )
            self.echo += self._rhythm_similarity_of_bars(
                self.bars[bar + 1], self.bars[bar + 3]
            )

    def _update_long_notes(self):
        self.long_notes = 0
        for bar in self.bars:
            for note in bar:
                if note.length == HALF:
                    self.long_notes += 1
                elif note.length >= QUARTER:
                    self.long_notes += 0.15

    def _update_neighboring_notes(self):
        self.neighboring_notes = 0
        notes = self.track.note
        for idx in range(len(notes) - 1):
            if abs(notes[idx].length - notes[idx + 1].length) == HALF - EIGHTH:
                self.neighboring_notes += 1

    @staticmethod
    def _rhythm_similarity_of_bars(bar1: List[Note], bar2: List[Note]):
        """Calculate the similarity of the rhythm of two bars."""
        same = 0
        for note1 in bar1:
            for note2 in bar2:
                if (note1.start_time - note2.start_time) % BAR_LENGTH == 0:
                    same += 1
        return (same**2) / (len(bar1) * len(bar2))


class GAForRhythm(TrackGABase):
    def __init__(self, population: List[Track], mutation_rate: float):
        super().__init__(population, mutation_rate)
        self.update_fitness()

    def get_fitness(self, track: Track) -> float:
        # It's better to have a higher fitness
        fitness = 0
        # give punishment if the number of strong beats is not enough
        param = RyhthmParameter(track)
        fitness += (param.strong_beats - 2 * self.bar_number) * theta
        # give encouragement if echo is high
        fitness += param.echo * delta
        # give punishment if there are strong notes on weak beats
        fitness -= param.strong_notes_on_weak_beats * epsilon
        # give punishment if there are too many long notes
        fitness -= param.long_notes * omiga
        # give punishment if there are too many neighboring notes
        # with large length gap
        fitness -= param.neighboring_notes * omicron
        return fitness

    def select(self):
        for i in range(len(self.fitness)):
            if self.fitness[i] > self.fitness[self.best_index]:
                self.best_index = i
                self.second_index = self.best_index
            elif self.fitness[i] > self.fitness[self.second_index]:
                self.second_index = i

    def crossover(self):
        for i in range(len(self.population)):
            index1 = self.best_index if randint(0, 1) else self.second_index
            index2 = self.best_index if randint(0, 1) else self.second_index
            bars1 = deepcopy(self.population[index1]).split_into_bars()
            bars2 = deepcopy(self.population[index2]).split_into_bars()
            cross_point = randint(0, self.bar_number // 2 - 1) * 2
            bars = bars1[:cross_point] + bars2[cross_point:]
            self.population[i] = self.population[i].join_bars(bars)

    def mutate(self):
        for i in range(len(self.population)):
            if random() > self.mutation_rate:
                continue
            # TODO: mutation
            track = deepcopy(
                self.population[choice([self.best_index, self.second_index])]
            )
            # When mutating, do not change the last note pitch,
            # because we want the last note to be the tonic.
            # Meanwhile, do not change the first note pitch in every bar,
            # in case of empty bars.
            mutate_type = choice_with_weight(
                [self._mutate_1, self._mutate_2, self._mutate_3, self._mutate_4],
                [mutation_rate_1, mutation_rate_2, mutation_rate_3, mutation_rate_4],
            )
            mutate_type(track)
            self.population[i] = track

    @staticmethod
    def _mutate_1(track: Track):
        # Swap two notes' length
        idx = randint(0, len(track.note) - 3)
        note1, note2 = track.note[idx], track.note[idx + 1]
        if note2.start_time // BAR_LENGTH != note1.start_time // BAR_LENGTH:
            # The two notes are in different bars, don't swap them
            return
        end = note2.end_time
        note1.length, note2.length = note2.length, note1.length
        note2.start_time = end - note2.length

    @staticmethod
    def _mutate_2(track: Track):
        # Split a note into two notes
        idx = randint(0, len(track.note) - 2)
        note = track.note[idx]
        if note.length == EIGHTH:  # We can't split it
            return
        while True:
            length = choice(NOTE_LENGTH)
            if length < note.length:
                end = note.end_time
                note.length -= length
                new_note = Note(note.pitch, length, end - length, note.velocity)
                track.note.insert(idx + 1, new_note)
                return

    @staticmethod
    def _mutate_3(track: Track):
        # merge two notes into one note
        idx = randint(0, len(track.note) - 3)
        note = track.note[idx]
        if track.note[idx + 1].start_time % BAR_LENGTH == 0:
            # The next note is at the beginning of a bar, we can't merge it
            return
        note.length = track.note[idx + 1].end_time - note.start_time
        track.note.pop(idx + 1)

    @staticmethod
    def _mutate_4(track: Track):
        # copy a bar and paste it to another bar
        idx = randint(2, track.bar_number - 1)
        bars = track.split_into_bars()
        bars[idx - 2] = deepcopy(bars[idx])
        for note in bars[idx - 2]:
            note.start_time -= BAR_LENGTH * 2
        track.join_bars(bars)

    def run(self, generation):
        print("Start training for rhythm...")
        for i in range(generation):
            if i % 10 == 0:
                print(f"Rhythm generation {i}:", end=" ")
                self.show_info()
            self.epoch()

            if self.fitness[self.best_index] > rhythm_target:
                print(f"[!] Target reached at generation {i}")
                print(f"final fitness for rhythm: {self.fitness[self.best_index]}")
                return self.population[self.best_index]

        print(f"[!] Target not reached after {generation} generations")
        print(f"final fitness for rhythm: {self.fitness[self.best_index]}")
        return self.population[self.best_index]
