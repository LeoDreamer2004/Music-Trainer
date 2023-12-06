from copy import deepcopy
from random import choice, randint, random
from typing import List
from midi.Track import *
from parameter.pitchParam import *
from GA.TrackParameter import TrackParameter

class GAForPitch:
    def __init__(
            self, reference_track: Track, population: List[Track], mutation_rate: float
    ):
        self.ref_track = reference_track
        self.ref_param = TrackParameter(self.ref_track)
        self.ref_param.update_pitch_parameters()
        self.population = population
        self.mutation_rate = mutation_rate
        self.fitness = [0] * len(population)
        self._update_fitness()
        self.best_index, self.second_index = 0, 0
        self.has_three_note_fitness = three_note_fitness
    
    
    def _update_fitness(self):
        for idx, track in enumerate(self.population):
            self.fitness[idx] = self._get_fitness(track)
    
    def _get_fitness(self, track: Track) -> float:
        # It's better to have a lower fitness
        track_param = TrackParameter(track)
        track_param.update_pitch_parameters()
        mean_diff = np.abs(track_param.means - self.ref_param.means)
        f1 = alpha * np.dot(mean_coeff, mean_diff)
        standard_diff = np.abs(track_param.standard - self.ref_param.standard)
        f2 = beta * np.dot(standard_coeff, standard_diff)
        g = gamma * TrackParameter(track).bad_notes
        
        if three_note_fitness:
            f3 = track_param.three_note_score * delta
        else:
            f3 = 0
        
        return f1 + f2 + g + f3
    
    def select(self):
        self._update_fitness()
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
    
    def show_info(self):
        print("Now the best fitness is", self.fitness[self.best_index])
    
    def run(self, generation: int):
        best_track = deepcopy(self.population[self.best_index])
        best_fitness = float("inf")
        for i in range(generation):
            if i % 30 == 0:
                print(f"Pitch generation {i}:", end=" ")
                self.show_info()
            self.select()
            self.crossover()
            self.mutate()
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
