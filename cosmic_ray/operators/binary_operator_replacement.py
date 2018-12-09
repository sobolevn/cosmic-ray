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
        "An operator that replaces binary {} with binary {}.".format(from_name, to_name)

        def mutation_count(self, node):
            if isinstance(node, parso.python.tree.Operator):
                # TODO: Need to check that node.parent isn't a 'factor' node. A factor parent indicates a unary op.
                if node.value == from_op:
                    return 1
            return 0

        def mutate(self, node, _):
            node.value = to_op
            return node

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
    return _MUTATION_OPERATORS
