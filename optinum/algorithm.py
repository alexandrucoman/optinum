"""
Implementation of the algorithms used for solving problemes.
"""
import abc
import random
import six

from optinum.data import Chromosome


@six.add_metaclass(abc.ABCMeta)
class Algorithm(object):

    def __init__(self, objective_function, variables, search_space):
        self._objective_function = objective_function
        self._search_space = search_space
        self._variables = variables
        self._name = self.__class__.__name__
        self._result = {}

    @property
    def name(self):
        return self._name

    @property
    def space(self):
        return self._search_space

    @property
    def objective_function(self):
        return self._objective_function

    @property
    def variables(self):
        return self._variables

    @property
    def result(self):
        return self._result

    @abc.abstractmethod
    def compute(self):
        pass

    @abc.abstractmethod
    def prepare_result(self, error):
        pass

    def run(self):
        try:
            self.compute()
        except (IndexError, ValueError, TypeError) as exc:
            self.prepare_result(exc)
        self.prepare_result(False)


@six.add_metaclass(abc.ABCMeta)
class HillClimbing(Algorithm):

    def __init__(self, objective_function, variables, search_space,
                 max_evaluations=50):
        super(HillClimbing, self).__init__(objective_function, variables,
                                           search_space)
        self._evaluations = 1
        self._max_evaluations = max_evaluations
        self._chromosome = None
        self._score = None

    @property
    def depth_search(self):
        return True

    @abc.abstractmethod
    def move_operator(self):
        pass

    def evaluate(self, chromosome):
        return self.objective_function.compute(chromosome)

    def update_chromosome(self, chromosome, score):
        self._chromosome = chromosome
        self._score = score

    def prepare_result(self, error):
        if error:
            return

        self._result = {
            'max_evaluations': self._max_evaluations,
            'evaluations': self._evaluations,
            'chromosome': self._chromosome,
            'score': self._score
        }

    def compute(self):
        self._chromosome = Chromosome.random(self.variables, self.space)
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

    @property
    def depth_search(self):
        return False

    def move_operator(self):
        genetic_info = self._chromosome.get_raw_data()
        index_list = range(len(genetic_info))
        random.shufle(index_list)
        for index in index_list:
            hamming_neighbor = list(genetic_info)
            hamming_neighbor[index] = int(not(genetic_info[index]))
            yield Chromosome.from_raw(hamming_neighbor, self.space)


class HCBestImprovement(HillClimbing):

    @property
    def depth_search(self):
        return True

    def move_operator(self):
        genetic_info = self._chromosome.get_raw_data()
        for index in range(len(genetic_info)):
            hamming_neighbor = list(genetic_info)
            hamming_neighbor[index] = int(not(genetic_info[index]))
            yield Chromosome.from_raw(hamming_neighbor, self.space)
