"""Implementation of the binary-operator-replacement operator.
"""

import itertools

import parso

from .operator import Operator, replacement_operator


_BINARY_OPERATORS = (
    ('+', 'Add'),
    ('-', 'Sub'),
    ('*', 'Mul'),
    ('/', 'Div'),
    ('//', 'FloorDiv'),
    ('%', 'Mod'),
    ('**', 'Pow'),
    ('>>', 'RShift'),
    ('<<', 'LShift'),
    ('|', 'BitOr'),
    ('&', 'BitAnd'),
    ('^', 'BitXor'),
)


def _create_replace_binary_operator(from_op, from_name, to_op, to_name):
    @replacement_operator(from_op, from_name, to_op, to_name)
    class ReplaceBinaryOperator(Operator):
        """An operator that replaces binary operators."""

        def mutation_count(self, node):
            if isinstance(node, parso.python.tree.Operator):
                if node.value == self.from_op:
                    return 1 
            return 0

        def mutate(self, node, _):
            node.value = self.to_op
            return node

    return ReplaceBinaryOperator

# Build all of the binary replacement operators
_MUTATION_OPERATORS = tuple(
    _create_replace_binary_operator(from_op, from_name, to_op, to_name)
    for (from_op, from_name), (to_op, to_name)
    in itertools.permutations(_BINARY_OPERATORS, 2))

# Inject the operators into the module namespace
for op in _MUTATION_OPERATORS:
    globals()[op.__name__] = op


def operators():
    "Iterable of all binary operator replacement mutation operators."
    return iter(_MUTATION_OPERATORS)
