"Implementation of the remove-decorator operator."

import parso
from parso.python.tree import Decorator

from .operator import Operator


class RemoveDecorator(Operator):
    """An operator that removes decorators."""

    def mutation_count(self, node):
        if isinstance(node, Decorator):
            return 1
        return 0

    def mutate(self, node, index):
        assert isinstance(node, Decorator)
        assert index == 0
        return None
