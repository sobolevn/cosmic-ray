"""Implementation of the unary-operator-replacement operator.
"""

from itertools import permutations

import parso.python.tree 

from .operator import Operator
from .util import extend_name

_UNARY_OPERATORS = (
    ('+', 'UAdd'),
    ('-', 'USub'),
    ('~', 'Invert'),
    ('not', 'Not'),
)

# TODO: Add support for removing operators

def _create_replace_unary_operators(from_op, from_name, to_op, to_name):
    @extend_name('_{}_{}'.format(from_name, to_name))
    class ReplaceUnaryOperator(Operator):
        "An operator that replaces unary {} with unary {}.".format(from_name, to_name)

        def mutation_count(self, node):
            if self._is_unary_operator(node):
                if node.value == from_op:
                    return 1
            return 0

        def mutate(self, node, index):
            assert index == 0
            assert self._is_unary_operator(node)
            node.value = to_op
            return node

        @staticmethod
        def _is_unary_operator(node):
            if isinstance(node, parso.python.tree.Operator):
                if node.parent.type == 'factor':
                    return True
            return False

    return ReplaceUnaryOperator


_MUTATION_OPERATORS = tuple(
    _create_replace_unary_operators(from_op, from_name, to_op, to_name)
    for (from_op, from_name), (to_op, to_name)
    in permutations(_UNARY_OPERATORS, 2))


for op_cls in _MUTATION_OPERATORS:
    globals()[op_cls.__name__] = op_cls


def operators():
    return _MUTATION_OPERATORS
