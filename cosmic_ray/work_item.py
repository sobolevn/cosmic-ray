"""A `WorkItem` carries information about potential and completed work in the
Cosmic Ray system.

`WorkItem` is one of the central structures in CR. It can describe both work
to be done and work that has been done, and it indicates how test sessions have
completed.
"""
import json
import pathlib


class WorkItem:
    def __init__(self,
                 data=None,
                 test_outcome=None,
                 worker_outcome=None,
                 diff=None,
                 module_path=None,
                 operator=None,
                 occurrence=None,
                 line_number=None,
                 col_offset=None,
                 command_line=None,
                 job_id=None):
        self.data = data
        self.test_outcome = test_outcome
        self.worker_outcome = worker_outcome
        self.diff = diff
        self.module_path = module_path
        self.operator = operator
        self.occurrence = occurrence
        self.line_number = line_number
        self.col_offset = col_offset
        self.command_line = command_line
        self._job_id = job_id

    @property
    def module_path(self):
        "Path to module being mutated."
        return self._module_path

    @module_path.setter
    def module_path(self, p):
        self._module_path = None if p is None else pathlib.Path(p)

    @property
    def job_id(self):
        "The unique ID of the job"
        return self._job_id

    def as_dict(self):
        """Get fields as a dict.
        """
        return {
            'data': self.data,
            'test_outcome': self.test_outcome,
            'worker_outcome': self.worker_outcome,
            'diff': self.diff,
            'module_path': str(self.module_path),
            'operator': self.operator,
            'occurrence': self.occurrence,
            'line_number': self.line_number,
            'col_offset': self.col_offset,
            'command_line': self.command_line,
            'job_id': self.job_id,
        }


class WorkItemJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, WorkItem):
            return {
                "_type": "WorkItem",
                "values": o.as_dict()
            }
        return super().default(o)


class WorkItemJsonDecoder(json.JSONDecoder):

    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook)

    def object_hook(self, obj):
        if ('_type' in obj) and (obj['_type'] == 'WorkItem') and ('values' in obj):
            values = obj['values']
            return WorkItem(**values)
        return obj
