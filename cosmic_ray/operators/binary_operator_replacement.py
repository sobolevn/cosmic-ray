"""Implementation of the binary-operator-replacement operator.
"""

import itertools

import parso

from .operator import Operator
from .util import extend_name


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
    @extend_name('_{}_{}'.format(from_name, to_name))
    class ReplaceBinaryOperator(Operator):
        """An operator that replaces binary operators."""

        def mutation_count(self, node):
            # TODO: Would node.type == 'operator' be better?
            if isinstance(node, parso.python.tree.Operator):
                if node.value == self.from_op:
                    return 1 
            return 0

        def mutate(self, node, _):
            node.value = self.to_op
            return node

    ReplaceBinaryOperator.to_op = to_op
    ReplaceBinaryOperator.from_op = from_op

    return ReplaceBinaryOperator

# Build all of the binary replacement operators
_MUTATION_OPERATORS = tuple(
    _create_replace_binary_operator(from_op, from_name, to_op, to_name)
    for (from_op, from_name), (to_op, to_name) 
    in itertools.permutations(_BINARY_OPERATORS, 2))

# Inject operators into module namespace
for op_cls in _MUTATION_OPERATORS:
    globals()[op_cls.__name__] = op_cls


def operators():
    "Iterable of all binary operator replacement mutation operators."
    return iter(_MUTATION_OPERATORS)
