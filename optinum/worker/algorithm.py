from optinum import config
from optinum.worker import base


class Algorithm(base.BaseWorker):

    def __init__(self, debug=config.MISC.DEBUG):
        super(Algorithm, self).__init__(debug=debug, delay=0, loop=False,
                                        name=None)
        self._status = config.STATUS.NOSET
        self._task = None

    @property
    def name(self):
        return self._name

    @property
    def status(self):
        return self._status

    @property
    def task(self):
        return self._task

    @task.setter
    def task(self, task):
        self._task = task

    def task_done(self, task, result):
        """What to execute after successfully finished processing a task."""
        super(Algorithm, self).task_done(task, result)
        self._status = config.STATUS.DONE

    def task_fail(self, task, exc):
        """What to do when the program fails processing a task."""
        super(Algorithm, self).task_fail(task, exc)
        self._status = config.STATUS.ERROR

    def prologue(self):
        """Executed once before the main procedures."""
        super(Algorithm, self).prologue()
        self._status = config.STATUS.RUNNING

    def epilogue(self):
        """Executed once after the main procedures."""
        self._status = config.STATUS.DONE
        # TODO(alexandrucoman): Prepare the result
        super(Algorithm, self).epilogue()

    def task_generator(self):
        """Override this with your custom task generator."""
        if self.task:
            yield
