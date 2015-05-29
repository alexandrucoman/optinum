from prettytable import PrettyTable

from optinum.analysis import base
from optinum.common import config


class HCAnalysis(base.Analysis):

    def __init__(self):
        super(HCAnalysis, self).__init__()

    def _report_header(self):
        table = PrettyTable(header=False)
        table.add_row(["Algorithm", self._algorithm])
        table.add_row(["Objective function", self._task.objective])
        table.add_row(["Variables", self._task.variables])
        table.add_row(["Space", self._task.search_space])
        return table

    def _report_content(self):
        table = PrettyTable(["No.", "Evaluations", "Score"])
        for index, task in enumerate(self._tasks.values()):
            if task.status != config.STATUS.ERROR:
                # TODO(alexandrucoman): Add row
                pass
            else:
                table.add_row([index, '-', 'Error'])

    def _get_task(self):
        pass

    def report(self):
        header = self._report_header()
        content = self._report_content()
        print(header)
        print(content)
