import threading

from optinum import config
from optinum import daemon


class Executor(daemon.ThreadDaemon):

    def __init__(self, name=None, debug=config.MISC.DEBUG,
                 delay=config.DAEMON.DELAY, loop=config.DAEMON.LOOP,
                 qsize=config.DAEMON.QSIZE, wcount=config.DAEMON.WORKERS):
        super(Executor, self).__init__(qsize, wcount, name, debug, delay, loop)
        self._task_lock = threading.Lock()
        self._jobs = []

    def task_done(self, task, result):
        """What to execute after successfully finished processing a task."""
        task.done(status=True, result=result)

    def task_fail(self, task, exc):
        """What to do when the program fails processing a task."""
        task.done(status=False, result=exc)

    def process(self, task):
        task.start()

    def add_task(self, task):
        with self._task_lock:
            self._jobs.append(task)

    def task_generator(self):
        with self._task_lock:
            if self._jobs:
                yield self._tasks.pop()
