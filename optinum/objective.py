"""
Collection of objective functions which will be optimized.
"""
import abc
import math
import six

cos = math.cos
pi = math.pi
sqrt = math.sqrt


@six.add_metaclass(abc.ABCMeta)
class Objective(object):

    def __init__(self):
        self._name = self.__class__.__name__

    @property
    def name(self):
        return self._name

    def compute(self, chromosome):
        variables = []
        genes = chromosome.get_genes()
        for gene in genes:
            variables.append(gene.value())

        return self.evaluate(variables)

    @abc.abstractmethod
    def evaluate(self, variables):
        pass
