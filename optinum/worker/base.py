"""Base classes for workers."""
# pylint: disable=abstract-method

import abc
import six
import time
import threading
try:
    import queue
except ImportError:
    import Queue as queue

from optinum.common import utils

LOG = utils.get_logger(__name__)


@six.add_metaclass(abc.ABCMeta)
class BaseWorker(object):

    def prologue(self):
        """Executed once before the main procedures."""
        pass

    def epilogue(self):
        """Executed once after the main procedures."""
        pass

    def task_done(self, task, result):
        """What to execute after successfully finished processing a task."""
        pass

    def task_fail(self, task, exc):
        """What to do when the program fails processing a task."""
        pass

    @abc.abstractmethod
    def process(self, task):
        """Override this with your desired procedures."""
        pass

    def start(self, task):
        """Starts a series of workers and processes incoming tasks."""
        self.prologue()
        try:
            self.process(task)
        except Exception as exc:
            self.task_fail(task, exc)
        else:
            self.task_done(task, exc)
        self.epilogue()


class Worker(BaseWorker):

    """Abstract base class for simple workers."""

    def __init__(self, debug, delay, loop, name=None):
        """Setup a new instance."""
        # refine name
        if not name:
            name = self.__class__.__name__

        # save the attributes
        self.name = name
        self.debug = debug
        self.delay = delay
        self.loop = loop

        self.stop = None    # event telling that all the things must end

    @abc.abstractmethod
    def task_generator(self):
        """Override this with your custom task generator."""
        pass

    def _process(self, task):
        """Wrapper over the `process`."""
        # pylint: disable=W0703
        try:
            result = self.process(task)
        except Exception as exc:
            self.task_fail(task, exc)
        else:
            self.task_done(task, result)

    def put_task(self, task):
        """Adds the task in the queue."""
        self._process(task)

    def finished(self):
        """What to execute after finishing processing all the tasks."""
        return self.loop    # decide to continue reprocessing or not

    def interrupted(self):
        """What to execute when keyboard interrupts arrive."""
        pass

    def start(self):
        """Starts a series of workers and processes incoming tasks."""
        self.prologue()
        while not self.stop.is_set():
            try:
                for task in self.task_generator():
                    self.put_task(task)
                loop = self.finished()
                if not loop:
                    break
                time.sleep(self.delay)
            except KeyboardInterrupt:
                self.interrupted()
                break
        self.epilogue()


class ConcurrentWorker(Worker):

    """Abstract base class for concurrent workers.

    Not inherited directly into final classes.
    """

    def __init__(self, qsize, wcount, *args, **kwargs):
        """Partial setup the new concurrent instance.

        :param qsize: maximum allowed queue size
        :type qsize: int
        :param wcount: desired number of workers
        :type wcount: int
        """
        super(ConcurrentWorker, self).__init__(*args, **kwargs)
        self.wcount = wcount     # desired number of workers
        self.qsize = qsize       # maximum allowed queue size
        self.workers = list()    # workers as objects
        self.manager = None      # who supervises the workers
        self.queue = queue.Queue(self.qsize)
        self.stop = threading.Event()

    def start_worker(self):
        """Create a custom worker (thread/process) and return its object."""
        worker = threading.Thread(target=self.work)
        worker.setDaemon(True)
        worker.start()
        return worker

    def manage_workers(self):
        """Maintain a desired number of workers up."""
        while not self.stop.is_set():
            for worker in self.workers[:]:
                if not worker.is_alive():
                    self.workers.remove(worker)

            if len(self.workers) == self.wcount:
                time.sleep(self.delay)
                continue

            worker = self.start_worker()
            self.workers.append(worker)

    def prologue(self):
        """Start a parallel supervisor."""
        super(ConcurrentWorker, self).prologue()

        self.manager = threading.Thread(target=self.manage_workers)
        self.manager.start()

    def epilogue(self):
        """Wait for that supervisor and its workers."""
        self.manager.join()
        for worker in self.workers:
            if worker.is_alive():
                worker.join()

        super(ConcurrentWorker, self).epilogue()

    def interrupted(self):
        """Mark the processing as stopped."""
        self.stop.set()
        super(ConcurrentWorker, self).interrupted()

    def put_task(self, task):
        """Adds a task to the queue."""
        self.queue.put(task)

    def get_task(self):
        """Retrieves a task from the queue."""
        while not self.stop.is_set():
            try:
                task = self.queue.get(block=True, timeout=self.delay)
            except queue.Empty:
                continue
            return task

    def task_done(self, task, result):
        self.queue.task_done()
        super(ConcurrentWorker, self).task_done(task, result)

    def work(self):
        """Worker able to retrieve and process tasks."""
        while not self.stop.is_set():
            task = self.get_task()
            if not task:
                continue
            self._process(task)
