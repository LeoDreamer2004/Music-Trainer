from GA.TrackParameter import TrackParameter
from typing import List
from midi.Track import Track
from midi.Note import Note
from copy import deepcopy
from random import randint, random, choice
from param import *


class TrackPopulation:
    
    def __init__(self,
                 reference_track: Track,
                 population: List[Track],
                 mutation_rate: float
                 ):
        
        self.ref_track = reference_track
        self.ref_param = TrackParameter(self.ref_track)
        self.population = population
        self.mutation_rate = mutation_rate
        self.fitness = [0] * len(population)
        self.best_index, self.second_index = 0, 0
        self.has_three_note_fitness = three_note_fitness
    
    def _update_fitness(self):
        for idx, track in enumerate(self.population):
            self.fitness[idx] = self._get_fitness(track)
    
    def _get_fitness(self, track: Track) -> float:
        # It's better to have a lower fitness
        track_param = TrackParameter(track)
        mean_diff = np.abs(track_param.means - self.ref_param.means)
        f1 = alpha * np.dot(mean_coeff, mean_diff)
        standard_diff = np.abs(track_param.standard - self.ref_param.standard)
        f2 = beta * np.dot(standard_coeff, standard_diff)
        
        g = gamma * TrackParameter(track).bad_notes
        
        if three_note_fitness:
            f3 = track_param.three_note_score * delta
        else:
            f3 = 0
        
        if verbose:
            print(f1, f2, g, f3)
        return f1 + f2 + g + f3
    
    
    def select(self):
        """Get the best and second best track"""
        self._update_fitness()
        for i in range(len(self.fitness)):
            if self.fitness[i] < self.fitness[self.best_index]:
                self.best_index = i
                self.second_index = self.best_index
            elif self.fitness[i] < self.fitness[self.second_index]:
                self.second_index = i
    
    def crossover(self):
        # for i in range(len(self.population)):
        #     index1 = self.best_index if randint(0,1) else self.second_index
        #     index2 = self.best_index if randint(0,1) else self.second_index
        #     bars1 = deepcopy(self.population[index1]).split_into_bars()
        #     bars2 = deepcopy(self.population[index2]).split_into_bars()
        #     cross_point = randint(0, self.ref_param.bar_number - 1)
        #     bars = bars1[:cross_point] + bars2[cross_point:]
        #     self.population[i] = self.population[i].join_bars(bars)
        # self._update_fitness()
        pass
    
    def mutate(self):
        for i in range(len(self.population)):
            if random() > self.mutation_rate:
                continue
            track = deepcopy(self.population[choice([self.best_index, self.second_index])])
            mutate_type = randint(1, mutation_rate_1 + mutation_rate_2 + mutation_rate_3)
            # When mutating, do not change the last note pitch,
            # because we want the last note to be the tonic
            if mutate_type <= mutation_rate_1:
                self._mutate_1(track)
            elif mutate_type <= mutation_rate_1 + mutation_rate_2:
                self._mutate_2(track)
            else:
                self._mutate_3(track)
            self.population[i] = track
    
    def _mutate_1(self, track: Track):
        for idx in range(len(track.note) - 1):
            if track.note[idx + 1].pitch - track.note[idx].pitch > 12:
                track.note[idx].pitch += 12
            elif track.note[idx + 1].pitch - track.note[idx].pitch < -12:
                track.note[idx].pitch -= 12
    
    def _mutate_2(self, track: Track):
        idx = randint(0, len(track.note) - 2)
        track.note[idx].pitch = Note.random_pitch_in_mode(track.key)
    
    def _mutate_3(self, track: Track):
        idx = randint(1, len(track.note) - 2)
        track.note[idx], track.note[idx - 1] = track.note[idx - 1], track.note[idx]
    
    def show_info(self):
        print("Now the best fitness is", self.fitness[self.best_index])
    
    def run(self, generation: int):
        
        for i in range(generation):
            if verbose:
                print(f"Generation {i}:")
            self.select()
            self.crossover()
            self.mutate()
            if verbose:
                self.show_info()
            if self.fitness[self.best_index] < target:
                print(f"[!] Target reached at generation {i}")
                print(f"final fitness: {self.fitness[self.best_index]}")
                return self.population[self.best_index]
        
        print(f"[!] Target not reached after {generation} generations")
        print(f"final fitness: {self.fitness[self.best_index]}")
        return self.population[self.best_index]
