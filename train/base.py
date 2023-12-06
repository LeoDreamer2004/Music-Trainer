from abc import ABCMeta, abstractmethod
import sys
from typing import List
from midoWrapper import *

sys.path.append("..")


class TrackParameterBase(metaclass=ABCMeta):
    """Used to calculate parameters of the tracks"""

    def __init__(self, track: Track):
        self.track = track
        self.bar_number = track.bar_number
        self.bars = self.track.split_into_bars()

    @abstractmethod
    def update_parameters(self):
        raise NotImplementedError


class TrackGABase(metaclass=ABCMeta):
    def __init__(self, population: List[Track], mutation_rate: float):
        self.population = population
        self.bar_number = population[0].bar_number
        self.mutation_rate = mutation_rate
        self.fitness = [0] * len(population)
        self.best_index, self.second_index = 0, 0

    def update_fitness(self):
        for idx, track in enumerate(self.population):
            self.fitness[idx] = self.get_fitness(track)

    @abstractmethod
    def get_fitness(self, track: Track) -> float:
        raise NotImplementedError

    @abstractmethod
    def select(self):
        raise NotImplementedError

    @abstractmethod
    def crossover(self):
        raise NotImplementedError

    @abstractmethod
    def mutate(self):
        raise NotImplementedError

    def show_info(self):
        print("Now the best fitness is", self.fitness[self.best_index])

    def epoch(self):
        self.update_fitness()
        self.select()
        self.crossover()
        self.mutate()

    @abstractmethod
    def run(self, generation):
        pass
