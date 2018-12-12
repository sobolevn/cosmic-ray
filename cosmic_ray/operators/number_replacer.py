"""Implementation of the NumberReplacer operator.
"""

import parso

from .operator import Operator


# List of offsets that we apply to numbers in the AST. Each index into the list
# corresponds to single mutation.
OFFSETS = [
    +1,
    -1,
]


class NumberReplacer(Operator):
    """An operator that modifies numeric constants."""

    def mutation_positions(self, node):
        if isinstance(node, parso.python.tree.Number):
            for _ in OFFSETS:
                yield (node.start_pos, node.end_pos)

    def mutate(self, node, index):
        """Modify the numeric value on `node`."""

        assert index < len(OFFSETS), 'received count with no associated offset'
        assert isinstance(node, parso.python.tree.Number)

        val = eval(node.value) + OFFSETS[index]
        return parso.python.tree.Number(' ' + str(val), node.start_pos)
