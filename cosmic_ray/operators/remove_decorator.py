"Implementation of the remove-decorator operator."

from parso.python.tree import Decorator

from .operator import Operator


class RemoveDecorator(Operator):
    """An operator that removes decorators."""

    def mutation_positions(self, node):
        if isinstance(node, Decorator):
            yield (node.start_pos, node.end_pos)

    def mutate(self, node, index):
        assert isinstance(node, Decorator)
        assert index == 0
        return None
