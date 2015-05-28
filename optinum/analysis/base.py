import abc
import time
import threading
import uuid
try:
    import queue
except ImportError:
    import Queue as queue

from optinum import factory
from optinum.common import config
from optinum.common import utils
from optinum.worker import base

LOG = utils.get_logger(__name__)


class Task(object):

    def __init__(self, algorithm, objective, precision, variables):
        self._id = uuid.uuid4()
        self._status = config.STATUS.NOSET
        self._algorithm = factory.algorithm(self.algorithm)
        self._objective = factory.objective_function(objective)(precision)
        self._precision = precision
        self._variables = variables

    @property
    def algorithm(self):
        return self._algorithm

    @property
    def objective(self):
        return self._objective

    @property
    def id(self):
        return self._id

    @property
    def variables(self):
        return self._variables

    @property
    def precision(self):
        return self._precision

    @property
    def status(self):
        return self._status

    def callback_fail(self, exc):
        self._status = config.STATUS.ERROR

    def callback_done(self):
        self._status = config.STATUS.DONE

    def is_done(self):
        return self._status == config.STATUS.DONE

    def run(self):
        self._status = config.STATUS.RUNNING
        self._algorithm.start(self)


class AlgorithmExecutor(base.ConcurrentWorker):

    def __init__(self, task_queue, *args, **kwargs):
        super(AlgorithmExecutor, self).__init__(*args, **kwargs)
        self._task_queue = task_queue
        self._tasks = {}

    def task_generator(self):
        """Retrieves a task from the queue."""
        while not self.stop.is_set():
            try:
                task = self._task_queue.get(block=True, timeout=self.delay)
                if task:
                    yield task
            except queue.Empty:
                continue

    def task_fail(self, task, exc):
        """What to do when the program fails processing a task."""
        super(AlgorithmExecutor, self).task_fail(task, exc)
        task.callback_fail(exc)

    def task_done(self, task, result):
        """What to execute after successfully finished processing a task."""
        super(AlgorithmExecutor, self).task_done(task, result)
        task.callback_done()

    def process(self, task):
        """Execute the current task."""
        task.run()


class Analysis(object):

    def __init__(self, command, executor=AlgorithmExecutor):
        self._task_queue = queue.Queue()
        self._command = command
        self._executor = executor(self._task_queue)

        self.stop = threading.Event()
        self.executor = threading.Thread(target=self._executor.start)
        self.executor.setDaemon(True)

    def _wait_for_tasks(self, tasks):
        LOG.debug("Waiting until the jobs are done.")
        while not self.stop.is_set():
            try:
                for task in tasks:
                    if not task.is_done:
                        break
                else:
                    return True
                time.sleep(config.REPORT.RETRY_INTERVAL)
            except KeyboardInterrupt:
                LOG.debug('Keyboard Interrupt received.')
                self.stop.set()

        return False

    @abc.abstractmethod
    def _get_task(self):
        pass

    @abc.abstractmethod
    def report(self):
        pass

    def prologue(self):
        """Executed once before the main procedures."""
        self.executor.start()

    def epilogue(self):
        """Executed once after the main procedures."""
        self._executor.stop.set()
        self.executor.join()

    def compute(self, execution_count):
        self.prologue()
        try:
            for index in range(execution_count):
                LOG.debug('Generate new task #%(index)s for: %(algorithm)s',
                          {"index": index, "algorithm": self._algorithm})
                task = self._get_task()        # Get a new task
                self.add_task(task)            # Add it to the processing queue
                self._tasks[task.id] = task    # Keep a link to it

            if not self._wait_for_tasks(self._tasks.values()):
                return False

            self.report()

        except Exception as exc:
            LOG.exception(exc)

        finally:
            self.epilogue()
