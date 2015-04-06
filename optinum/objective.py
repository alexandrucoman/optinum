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


class Rosenbrock(Objective):

    def evaluate(self, variables):
        result = 0
        for index in range(len(variables) - 1):
            result += 100 * (variables[index + 1] - variables[index] ** 2) ** 2
            result += (1 - variables[index]) ** 2
        return result


class Rastrigin(Objective):

    def evaluate(self, variables):
        result = 10 * len(variables)
        for index in range(len(variables)):
            result += variables[index] ** 2
            result -= 10 * cos(2 * pi * variables[index])
        return result


class Griewangk(Objective):

    def evaluate(self, variables):
        sum_, prod = 0, 1
        for index in range(len(variables)):
            sum_ += variables[index] ** 2 / 4000
            prod *= cos(variables[index] / sqrt(index))
        return sum_ - prod + 1


class SixHumpCamelBack(Objective):

    def evaluate(self, variables):
        if len(variables) != 2:
            raise ValueError("Invalid number of variables for %(name)s" %
                             {"name": self.name})
        result = (4 - 2.1 * variables[0] ** 2 + variables[0] ** 4 / 3)
        result *= variables[0] ** 2 + variables[0] * variables[1]
        result += (-4 + 4 * variables[1] ** 2) * variables[1] ** 2
        return result
