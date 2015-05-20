"""Base classes for workers."""
# pylint: disable=abstract-method

import abc
import collections
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

    def prologue(self):
        """Executed once before the main procedures."""
        pass

    def epilogue(self):
        """Executed once after the main procedures."""
        pass

    @abc.abstractmethod
    def task_generator(self):
        """Override this with your custom task generator."""
        pass

    @abc.abstractmethod
    def process(self, task):
        """Override this with your desired procedures."""
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

    def task_done(self, task, result):
        """What to execute after successfully finished processing a task."""
        pass

    def task_fail(self, task, exc):
        """What to do when the program fails processing a task."""
        pass

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


class ConcurrentWorker(BaseWorker):

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
        self.queue = None        # processing queue

    @abc.abstractmethod
    def start_worker(self):
        """Create a custom worker (thread/process) and return its object."""
        pass

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


class Dispatcher(ConcurrentWorker):

    """Base class for dispatching."""

    def __init__(self, listener, *args, **kwargs):
        """Init with custom values and take care of `listener` (server)."""
        super(Dispatcher, self).__init__(*args, **kwargs)
        self.listener = listener

    def epilogue(self):
        """Close server connection."""
        self.listener.close()
        super(Dispatcher, self).epilogue()

    def task_generator(self):
        """Listens for new requests (connections)."""
        # pylint: disable=W0703
        try:
            task = self.listener.accept()
            if task:
                yield task
        except Exception as exc:
            if str(exc).find("The pipe is being closed") == -1:
                LOG.error(exc)

    def put_task(self, task):
        """Pre-process the task as a new connection then add it
        in the queue.
        """
        _task = collections.namedtuple("Task", ["data", "raw_data", "socket"])

        try:
            _dict = task.recv()
        except EOFError:
            LOG.error("The pipe is being closed")
            return
        except Exception as exc:
            LOG.error("Error occurred while receiving: %(error)s",
                      {"error": exc})
            return

        query = collections.namedtuple("Query", _dict.keys())
        data = query(*_dict.values())

        super(Dispatcher, self).put_task(_task(data, _dict, task))

    def process(self, task):
        """Treats a preprocessed request."""
        try:
            function = "handle_{}".format(task.data.request)
        except AttributeError:
            raise ValueError("Missing the request field from request")

        try:
            func = getattr(self, function)
        except AttributeError:
            raise ValueError("Function {} not defined".format(function))

        try:
            response = func(task)
        except Exception as exc:
            LOG.exception(exc)
            raise

        return response

    def task_done(self, task, result):
        """Sends the response back."""
        try:
            task.socket.send(result)
        except EOFError as exc:
            LOG.error(exc)
        super(Dispatcher, self).task_done(task, result)

    def task_fail(self, task, exc):
        LOG.error(exc)
        super(Dispatcher, self).task_fail(task, exc)
