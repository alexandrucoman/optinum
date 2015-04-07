"""
Utilities for creating a report.
"""
import abc
import collections
import threading
import time

import six
from prettytable import PrettyTable

from optinum import config
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

        self._search_space = data.Space(start, stop, precision)
        if not self._search_space:
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
    def search_space(self):
        return self._search_space

    @property
    def start(self):
        return self._start

    @property
    def stop(self):
        return self._stop


class Job(object):

    _RESULT = collections.namedtuple('Result', ['status', 'data'])

    def __init__(self, algorithm, task, *args, **kwargs):
        algorithm = factory.get_algorithm(algorithm)
        if not algorithm:
            raise ValueError('Unsupported algorithm.')

        self._algorithm = algorithm(task.objective_function, task.variables,
                                    task.search_space, *args, **kwargs)
        self._task = task
        self._done = False
        self._status = False
        self._result = False

        self._lock = threading.Lock()

    @property
    def is_done(self):
        return self._done

    @property
    def result(self):
        return self._RESULT(self._status, self._algorithm.result)

    def done(self, status, result):
        self._done = True
        self._status = status
        if status:
            self._result = self._algorithm.result
        else:
            self._result = result

    def start(self):
        self._algorithm.run()


@six.add_metaclass(abc.ABCMeta)
class Report(object):

    def __init__(self, executor, algorithm, task):
        self._algorithm = algorithm
        self._executor = executor
        self._jobs = []
        self._stop_event = threading.Event()

    @abc.abstractmethod
    def _get_job(self):
        pass

    @abc.abstractmethod
    def _prepare_report(self):
        pass

    def _wait_for_jobs(self):
        while not self._stop_event.is_set():
            try:
                report_done = True
                for job in self._jobs:
                    if not job.is_done:
                        report_done = False
                        break
                if report_done:
                    return True
                time.sleep(config.REPORT.RETRY_INTERVAL)
            except KeyboardInterrupt:
                self._stop_event.set()

        return False

    def compute(self, execution_count):
        for index in range(execution_count):
            job = self._get_job()           # Get a new job
            self._executor.add_task(job)    # Add it to the processing queue
            self._jobs.append(job)          # Keep a link to it

        if not self._wait_for_jobs():
            return False

        return self._prepare_report


class HCReport(Report):

    def __init__(self, executor, algorithm, task, max_evaluations=50):
        super(HCReport, self).__init__(executor, algorithm, task)
        self._max_evaluation = max_evaluations

    def _get_job(self):
        return Job(self._algorithm, self._task,
                   max_evaluations=self._max_evaluation)

    def _report_header(self):
        table = PrettyTable(header=False)
        table.add_row(["Algorithm", self._algorithm])
        table.add_row(["Objective function", self._task.objective])
        table.add_row(["Variables", self._task.variables])
        table.add_row(["Space", self._task.search_space])
        return table

    def _report_content(self):
        table = PrettyTable(["No.", "Evaluations", "Score"])
        for index, job in enumerate(self._jobs):
            job_result = job.result
            if job_result.status:
                job_data = job_result.data
                table.add_row([index, job_data["evaluations"],
                              job_data["score"]])
            else:
                table.add_row([index, '-', 'Error'])

    def _prepare_report(self):
        header = self._report_header()
        content = self._report_content()
        print(header)
        print(content)
