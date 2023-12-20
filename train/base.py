import sys
from abc import ABCMeta, abstractmethod
from random import random
from typing import List
from midoWrapper import *

sys.path.append("..")


def choice_with_weight(choices_list: List, weighted_list: List[float]):
    """Randomly choose an element from choices_list with weight in weighted_list"""
    sum_weight = sum(weighted_list)
    rand = random() * sum_weight
    temp = 0
    for i, weight in enumerate(weighted_list):
        if temp <= rand < temp + weight:
            return choices_list[i]
        temp += weight
    return choices_list[-1]


class TrackParameterBase(metaclass=ABCMeta):
    """Base class for calculating parameters of the tracks"""

    def __init__(self, track: Track):
        self.settings = track.sts
        self.track = track
        self.bar_number = track.bar_number
        self.bars = self.track.split_into_bars()

    @abstractmethod
    def update_parameters(self):
        raise NotImplementedError


class TrackGABase(metaclass=ABCMeta):
    """Base class for GA"""

    def __init__(self, population: List[Track], mutation_rate: float):
        self.population = population
        self.bar_number = population[0].bar_number
        self.mutation_rate = mutation_rate
        self.fitness = [0] * len(population)
        self.best_index, self.second_index = 0, 0
        self.settings = population[0].sts

    def update_fitness(self):
        for idx, track in enumerate(self.population):
            self.fitness[idx] = self.get_fitness(track)

    @abstractmethod
    def get_fitness(self, track: Track) -> float:
        raise NotImplementedError

    def select(self):
        for i in range(len(self.fitness)):
            if self.fitness[i] > self.fitness[self.best_index]:
                self.best_index = i
                self.second_index = self.best_index
            elif self.fitness[i] > self.fitness[self.second_index]:
                self.second_index = i

    @abstractmethod
    def crossover(self):
        raise NotImplementedError

    @abstractmethod
    def mutate(self):
        raise NotImplementedError

    def train_info(self):
        return "Now the best fitness is " + str(self.fitness[self.best_index])

    def epoch(self):
        self.crossover()
        self.mutate()
        self.update_fitness()
        self.select()

    @abstractmethod
    def run(self, generation):
        pass
