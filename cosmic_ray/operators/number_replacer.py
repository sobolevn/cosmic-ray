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

    def mutation_count(self, node):
        if isinstance(node, parso.python.tree.Number):
            return len(OFFSETS)
        return 0

    def mutate(self, node, idx):
        """Modify the numeric value on `node`."""

        assert idx < len(OFFSETS), 'received count with no associated offset'
        assert isinstance(node, parso.python.tree.Number)

        val = eval(node.value) + OFFSETS[idx]
        return parso.parse(' ' + str(val))
