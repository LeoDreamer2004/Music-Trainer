from copy import deepcopy
from random import choice, randint, random
from midi.Track import Track
from midi.Note import Note
from typing import List
from parameter.const import *
from parameter.rhythmParam import *
from GA.TrackParameter import TrackParameter


class GAForRhythm:
    def __init__(self, population: List[Track], mutation_rate: float):
        self.population = population
        self.bar_number = population[0].bar_number
        self.mutation_rate = mutation_rate
        self.fitness = [0] * len(population)
        self._update_fitness()
        self.best_index, self.second_index = 0, 0
    
    def _update_fitness(self):
        for idx, track in enumerate(self.population):
            self.fitness[idx] = self._get_fitness(track)
    
    def _get_fitness(self, track: Track) -> float:
        # It's better to have a higher fitness
        fitness = 0
        # give punishment if the number of strong beats is not enough
        param = TrackParameter(track)
        param.update_rhythm_parameters()
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
        self._update_fitness()
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
            mutate_type = randint(1, mutation_rate_1 + mutation_rate_2 + mutation_rate_3 + mutation_rate_4)
            # When mutating, do not change the last note pitch,
            # because we want the last note to be the tonic.
            # Meanwhile, do not change the first note pitch in every bar,
            # in case of empty bars.
            if mutate_type <= mutation_rate_1:
                self._mutate_1(track)
            elif mutate_type <= mutation_rate_1 + mutation_rate_2:
                self._mutate_2(track)
            elif mutate_type <= mutation_rate_1 + mutation_rate_2 + mutation_rate_3:
                self._mutate_3(track)
            else:
                self._mutate_4(track)
            self.population[i] = track
    
    @staticmethod
    def _mutate_1(track: Track):
        """Swap two notes' length"""
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
        """Split a note into two notes"""
        # TODO: split long notes first to accelerate evolution speed
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
        """Merge two notes into one note"""
        idx = randint(0, len(track.note) - 3)
        note = track.note[idx]
        if track.note[idx + 1].start_time % BAR_LENGTH == 0:
            # The next note is at the beginning of a bar, we can't merge it
            return
        note.length = track.note[idx + 1].end_time - note.start_time
        track.note.pop(idx + 1)
    
    @staticmethod
    def _mutate_4(track: Track):
        """Copy a bar and paste it to another bar"""
        idx = randint(2, track.bar_number - 1)
        bars = track.split_into_bars()
        bars[idx - 2] = deepcopy(bars[idx])
        for note in bars[idx - 2]:
            note.start_time -= BAR_LENGTH * 2
        track.join_bars(bars)
    
    def show_info(self):
        print("Now the best fitness is", self.fitness[self.best_index])
    
    def run(self, generation):
        print("Start training for rhythm...")
        for i in range(generation):
            if i % 10 == 0:
                print(f"Rhythm generation {i}:", end=" ")
                self.show_info()
            self.select()
            self.crossover()
            self.mutate()
            
            if self.fitness[self.best_index] > rhythm_target:
                print(f"[!] Target reached at generation {i}")
                print(f"final fitness for rhythm: {self.fitness[self.best_index]}")
                return self.population[self.best_index]
        
        print(f"[!] Target not reached after {generation} generations")
        print(f"final fitness for rhythm: {self.fitness[self.best_index]}")
        return self.population[self.best_index]
