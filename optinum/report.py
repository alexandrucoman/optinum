"""
Utilities for creating a report.
"""
import threading

from optinum import data
from optinum import factory


class Task(object):

    def __init__(self, start, stop, precision, objective, variables):
        self._stop = stop
        self._start = start
        self._precision = precision
        self._objective = objective
        self._variables = variables

        self._objective_function = factory.objective_function(objective)
        if not self._objective_function:
            raise ValueError('Invalid name for the objective function.')

        self._space = data.Space(start, stop, precision)
        if not self._space:
            raise ValueError('Invalid information provided for the space.')

    @property
    def objective(self):
        return self._objective

    @property
    def objective_function(self):
        return self._objective_function

    @property
    def variables(self):
        return self._variables

    @property
    def precision(self):
        return self._precision

    @property
    def space(self):
        return self._space

    @property
    def start(self):
        return self._start

    @property
    def stop(self):
        return self._stop


class Job(object):

    def __init__(self, algorithm, task, **conf):
        algorithm = factory.get_algorithm(algorithm)
        if not algorithm:
            raise ValueError('Unsupported algorithm.')

        self._algorithm(**conf)
        self._task = task
        self._lock = threading.Lock()

    def start(self):
        self._algorithm.run()
