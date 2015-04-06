"""
Implementation of the algorithms used for solving problemes.
"""
import abc
import six


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
