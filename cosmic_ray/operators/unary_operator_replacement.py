"""Implementation of the unary-operator-replacement operator.
"""

from itertools import permutations

from parso.python.tree import Keyword, Operator, PythonNode

from . import operator
from .util import extend_name

_UNARY_OPERATORS = (
    ('+', 'UAdd'),
    ('-', 'USub'),
    ('~', 'Invert'),
    ('not', 'Not'),
    (None, 'Nothing'),
)

# TODO: Add support for removing operators


def _create_replace_unary_operators(from_op, from_name, to_op, to_name):
    if to_op is None:
        suffix = '_Delete_{}'.format(from_name)
    else:
        suffix = '_{}_{}'.format(from_name, to_name)

    @extend_name(suffix)
    class ReplaceUnaryOperator(operator.Operator):
        "An operator that replaces unary {} with unary {}.".format(
            from_name, to_name)

        def mutation_count(self, node):
            if _is_unary_operator(node):
                return 1
            return 0

        def mutate(self, node, index):
            assert index == 0
            assert _is_unary_operator(node)

            if to_op is None:
                del node.children[0]
            else:
                node.children[0].value = to_op
            return node

    return ReplaceUnaryOperator


def _is_factor(node):
    return (isinstance(node, PythonNode)
            and node.type in {'factor', 'not_test'}
            and len(node.children) > 0
            and isinstance(node.children[0],
                           Operator))


def _is_not_test(node):
    return (isinstance(node, PythonNode)
            and node.type == 'not_test'
            and len(node.children) > 0
            and isinstance(node.children[0], Keyword)
            and node.children[0].value == 'not')


def _is_unary_operator(node):
    return _is_factor(node) or _is_not_test(node)


_MUTATION_OPERATORS = tuple(
    _create_replace_unary_operators(from_op, from_name, to_op, to_name)
    for (from_op, from_name), (to_op, to_name)
    in permutations(_UNARY_OPERATORS, 2)
    if from_op is not None)


for op_cls in _MUTATION_OPERATORS:
    globals()[op_cls.__name__] = op_cls


def operators():
    return _MUTATION_OPERATORS
