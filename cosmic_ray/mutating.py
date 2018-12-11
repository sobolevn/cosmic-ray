from cosmic_ray.ast import Visitor


def _full_module_name(obj):
    return '{}.{}'.format(
        obj.__class__.__module__,
        obj.__class__.__name__)


class MutationVisitor(Visitor):
    def __init__(self, occurrence, operator):
        self.operator = operator
        self._occurrence = occurrence
        self._count = 0

    def visit(self, node):
        for index, _ in enumerate(self.operator.mutation_positions(node)):
            if self._count == self._occurrence:
                node = self.operator.mutate(node, index)
            self._count += 1

        return node
