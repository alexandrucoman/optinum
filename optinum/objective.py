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

    """Contract class for all the objective functions."""

    min_xi = 0
    max_xi = 0

    def __init__(self, precision):
        self._name = self.__class__.__name__
        self._precision = precision

    def __call__(self, chromosome):
        return self.compute(chromosome)

    @property
    def name(self):
        return self._name

    def compute(self, chromosome):
        variables = []
        genes = chromosome.get_genes()
        for gene in genes:
            variables.append(gene.value(self.min_xi, self._precision))

        return self.evaluate(variables)

    @abc.abstractmethod
    def evaluate(self, variables):
        pass


class Rosenbrock(Objective):

    """Rosenbrock's valley is a classic optimization problem, also known
    as Banana function.

    The global optimum is inside a long, narrow, parabolic shaped flat valley.
    To find the valley is trivial, however convergence to the global optimum
    is difficult and hence this problem has been repeatedly used in assess
    the performance of optimization algorithms.
    """

    min_xi = -2048
    max_xi = 2048

    def evaluate(self, variables):
        result = 0
        for index in range(len(variables) - 1):
            result += 100 * (variables[index + 1] - variables[index] ** 2) ** 2
            result += (1 - variables[index]) ** 2
        return result


class Rastrigin(Objective):

    """Rastrigin's function is based on function 1 with the addition of cosine
    modulation to produce many local minima.

    Thus, the test function is highly multimodal. However, the location of
    the minima are regularly distributed.
    """

    min_xi = -5.12
    max_xi = 5.21

    def evaluate(self, variables):
        result = 10 * len(variables)
        for index in range(len(variables)):
            result += variables[index] ** 2
            result -= 10 * cos(2 * pi * variables[index])
        return result


class Griewangk(Objective):

    """Griewangk's function is similar to Rastrigin's function.

    It has many widespread local minima. However, the location of
    the minima are regularly distributed.
    """

    min_xi = -600
    max_xi = 600

    def evaluate(self, variables):
        sum_, prod = 0, 1
        for index in range(len(variables)):
            sum_ += variables[index] ** 2 / 4000
            prod *= cos(variables[index] / sqrt(index))
        return sum_ - prod + 1


class SixHumpCamelBack(Objective):

    """The 2-D Six-hump camel back function [DS78] is a global
    optimization test function.

    Within the bounded region are six local minima, two of them
    are global minima.
    """

    min_xi = -2
    max_xi = 2

    def evaluate(self, variables):
        if len(variables) != 2:
            raise ValueError("Invalid number of variables for %(name)s" %
                             {"name": self.name})
        result = (4 - 2.1 * variables[0] ** 2 + variables[0] ** 4 / 3)
        result *= variables[0] ** 2 + variables[0] * variables[1]
        result += (-4 + 4 * variables[1] ** 2) * variables[1] ** 2
        return result
