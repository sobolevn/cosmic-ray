"Implementation of the zero-iteration-loop operator."

import parso
from parso.python.tree import ForStmt

from .operator import Operator


class ZeroIterationForLoop(Operator):
    """An operator that modified for-loops to have zero iterations."""

    def mutation_count(self, node):
        if isinstance(node, ForStmt):
            return 1
        return 0

    def mutate(self, node, index):
        """Modify the For loop to evaluate to None"""
        assert index == 0
        assert isinstance(node, ForStmt)

        empty_list = parso.parse(' []')
        node.children[3] = empty_list
        return node
