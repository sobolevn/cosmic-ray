"""Classes for describing work and results.
"""
import json
import pathlib


class WorkResult:
    """The result of a single mutation and test run.
    """
    def __init__(self,
                 data,
                 test_outcome,
                 worker_outcome,
                 diff):
        self.data = data
        self.test_outcome = test_outcome
        self.worker_outcome = worker_outcome
        self.diff = diff

    def as_dict(self):
        return {
            'data': self.data,
            'test_outcome': self.test_outcome,
            'worker_outcome': self.worker_outcome,
            'diff': self.diff,
        }

    def __eq__(self, rhs):
        return self.as_dict() == rhs.as_dict()

    def __neq__(self, rhs):
        return not self == rhs



class WorkItem:
    """Description of the work for a single mutation and test run.
    """
    def __init__(self,
                 module_path=None,
                 operator=None,
                 occurrence=None,
                 line_number=None,
                 col_offset=None,
                 job_id=None):
        self.module_path = module_path
        self.operator = operator
        self.occurrence = occurrence
        self.line_number = line_number
        self.col_offset = col_offset
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
            'module_path': str(self.module_path),
            'operator': self.operator,
            'occurrence': self.occurrence,
            'line_number': self.line_number,
            'col_offset': self.col_offset,
            'job_id': self.job_id,
        }

    def __eq__(self, rhs):
        return self.as_dict() == rhs.as_dict()

    def __neq__(self, rhs):
        return not self == rhs


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


class WorkResultsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, WorkItem):
            return {
                "_type": "WorkResult",
                "values": o.as_dict()
            }
        return super().default(o)


class WorkResultJsonDecoder(json.JSONDecoder):

    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook)

    def object_hook(self, obj):
        if ('_type' in obj) and (obj['_type'] == 'WorkResult') and ('values' in obj):
            values = obj['values']
            return WorkResult(**values)
        return obj
