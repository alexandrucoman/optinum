import threading
try:
    import queue
except ImportError:
    import Queue as queue

from optinum import config
from optinum import daemon
from optinum import log


class Executor(daemon.ThreadDaemon):

    def __init__(self, name=None, debug=config.MISC.DEBUG,
                 delay=config.DAEMON.FINEDELAY, loop=config.DAEMON.LOOP,
                 qsize=config.DAEMON.QSIZE, wcount=config.DAEMON.WORKERS):
        super(Executor, self).__init__(qsize, wcount, name, debug, delay, loop)
        self._jobs = queue.Queue(0)

    def prologue(self):
        """Start a parallel supervisor."""
        super(Executor, self).prologue()
        log.debug("The Executor is starting...")

    def epilogue(self):
        """Wait for that supervisor and its workers."""
        log.debug("The Executor is shuting down.")
        super(Executor, self).epilogue()

    def task_done(self, task, result):
        """What to execute after successfully finished processing a task."""
        log.debug('The task %(task)s returns: %(result)s' %
                  {"task": task, "result": result})
        task.done(status=True, result=result)

    def task_fail(self, task, exc):
        """What to do when the program fails processing a task."""
        log.debug("Failed to process task %(task)s: %(reason)s",
                  {"task": task, "reason": exc})
        task.done(status=False, result=exc)

    def process(self, task):
        log.debug("Processing task: %(task)s", {"task": task})
        task.start()

    def add_task(self, task):
        log.debug("The task: %(task)s was added to queue.",
                  {"task": task})
        self._jobs.put(task)

    def task_generator(self):
        while not self.stop.is_set():
            try:
                task = self._jobs.get(block=True, timeout=self.delay)
                yield task
            except queue.Empty:
                yield None


class ExecutorThread(threading.Thread):
    def __init__(self):
        super(ExecutorThread, self).__init__()
        self._executor = Executor()

    def add_task(self, task):
        self._executor.add_task(task)

    def run(self):
        self._executor.start()
