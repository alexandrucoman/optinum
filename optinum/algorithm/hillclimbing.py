import abc
import random

import six

from optinum.algorithm import base
from optinum.common import objects

__all__ = ['HCFirstImprovement', 'HCBestImprovement']


@six.add_metaclass(abc.ABCMeta)
class HillClimbing(base.Algorithm):

    def __init__(self, name="HillClimbing", max_evaluations=50):
        super(HillClimbing, self).__init__(name)
        self._evaluations = 1
        self._max_evaluations = max_evaluations

    @property
    def depth_search(self):
        return True

    @abc.abstractmethod
    def move_operator(self):
        pass

    def evaluate(self, chromosome):
        return self.task.objective_function.compute(chromosome)

    def update_chromosome(self, chromosome, score):
        self._chromosome = chromosome
        self._score = score

    def process(self, task):
        self._chromosome = objects.Chromosome.random(task.variables,
                                                     task.space)
        self._score = self.evaluate(self._chromosome)
        self._evaluations = 1
        while self._evaluations < self._max_evaluations:
            move_made = False
            for candidate_chromosome in self.move_operator():
                candidate_score = self.evaluate(candidate_chromosome)
                if candidate_score < self._score:
                    move_made = True
                    self.update_chromosome(candidate_chromosome,
                                           candidate_score)
                    if not self.depth_search:
                        break

            self._evaluations = self._evaluations + 1
            if not move_made and self.depth_search:
                break


class HCFirstImprovement(HillClimbing):

    def __init__(self, name="HillClimbing: First Improvement"):
        super(HCFirstImprovement, self).__init__(name=name)

    @property
    def depth_search(self):
        return False

    def move_operator(self):
        genetic_info = self._chromosome.get_raw_data()
        index_list = range(len(genetic_info))
        random.shuffle(index_list)
        for index in index_list:
            hamming_neighbor = list(genetic_info)
            hamming_neighbor[index] = int(not(genetic_info[index]))
            yield objects.Chromosome.from_raw(hamming_neighbor, self.space)


class HCBestImprovement(HillClimbing):

    def __init__(self, name="HillClimbing: Best Improvement"):
        super(HCFirstImprovement, self).__init__(name=name)

    @property
    def depth_search(self):
        return True

    def move_operator(self):
        genetic_info = self._chromosome.get_raw_data()
        for index in range(len(genetic_info)):
            hamming_neighbor = list(genetic_info)
            hamming_neighbor[index] = int(not(genetic_info[index]))
            yield objects.Chromosome.from_raw(hamming_neighbor, self.space)
