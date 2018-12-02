from cosmic_ray.ast import OperatorVisitor


def _full_module_name(obj):
    return '{}.{}'.format(
        obj.__class__.__module__,
        obj.__class__.__name__)


class MutationVisitor(OperatorVisitor):
    def __init__(self, occurrence, operator):
        super().__init__(operator)
        self._occurrence = occurrence
        self._count = 0
        self._activation_record = None

    @property
    def activation_record(self):
        return self._activation_record

    def activate(self, node, num_mutations):
        if self._count <= self._occurrence < self._count + num_mutations:
            assert self.activation_record is None
            assert self._occurrence - self._count < num_mutations

            self._activation_record = {
                'operator': _full_module_name(self.operator),
                'occurrence': self._occurrence,
                'line_number': node.start_pos[0]
            }

            node = self.operator.mutate(node, self._occurrence - self._count)
        
        self._count += num_mutations
        return node
