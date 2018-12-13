"""This module contains mutation operators which replace one
comparison operator with another.
"""
import itertools

import parso.python.tree

from .operator import Operator
from .util import extend_name


_OPERATOR_DESCRIPTIONS = (
    ('==', 'Eq'),
    ('!=', 'NotEq'),
    ('<', 'Lt'),
    ('<=', 'LtE'),
    ('>', 'Gt'),
    ('>=', 'GtE'),
    ('is', 'Is'),
    ('is not', 'IsNot'),
)


def _create_operator(from_op, from_op_name, to_op, to_op_name):
    @extend_name('_{}_{}'.format(from_op_name, to_op_name))
    class ReplaceComparisonOperator(Operator):
        "An operator that replaces {} with {}".format(from_op_name, to_op_name)

        def mutation_positions(self, node):
            if node.type == 'comparison':
                # Every other child starting at 1 is a comparison operator of some sort
                for comparison_op in node.children[1::2]:
                    if comparison_op.get_code().strip() == from_op:
                        yield (comparison_op.start_pos, comparison_op.end_pos)

        def mutate(self, node, index):
            mutated_comparison_op = parso.parse(' ' + to_op)
            node.children[index * 2 + 1] = mutated_comparison_op
            return node

    return ReplaceComparisonOperator

# Build all of the binary replacement operators
_OPERATORS = tuple(
    _create_operator(from_op, from_name, to_op, to_name)
    for (from_op, from_name), (to_op, to_name)
    in itertools.permutations(_OPERATOR_DESCRIPTIONS, 2))

# Inject the operators into the module namespace
for op_cls in _OPERATORS:
    globals()[op_cls.__name__] = op_cls


def operators():
    "Iterable of all binary operator replacement mutation operators."
    return iter(_OPERATORS)

# TODO: We have some complex exceptions that we need to take care of. Here's the
# old code that did that.
#
# # Maps from-ops to to-ops when the RHS is `None`
# _RHS_IS_NONE_OPS = {ast.Eq: [ast.IsNot], ast.NotEq: [ast.Is], ast.Is:
#     [ast.IsNot], ast.IsNot: [ast.Is],
# }

# _RHS_IS_INTEGER_OPS = (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE)


# def _rhs_is_none_ops(from_op):
#     assert issubclass(from_op, ast.AST)
#     return _RHS_IS_NONE_OPS.get(from_op, ())


# def _rhs_is_integer_ops(from_op):
#     assert issubclass(from_op, ast.AST)
#     return _RHS_IS_INTEGER_OPS


# def _comparison_rhs_is_none(node):
#     "Determine if the node is a comparison with `None` on the RHS."
#     return ((len(node.comparators) == 1)
#             and
#             (compare_ast(node.comparators[0], ast.NameConstant(None))))


# def _comparison_rhs_is_integer(node):
#     return ((len(node.comparators) == 1)
#             and
#             isinstance(node.comparators[0], ast.Num))


# def _build_mutations(node):
#     """Given a Compare node, produce the list of mutated operations.
#     Depending on the details of the Compare node, different tactics
#     may be used to generate the list of mutations, in order to avoid
#     generating mutants which we know will be incompetent.
#     Args:
#         node: A Compare node.
#     Returns:
#         A sequence of (idx, to-op) tuples describing the mutations for `ops`.
#         The idx is the index into the list of ops for the Compare node
#         (A single Compare node can contain multiple operators in order to
#         represent expressions like 5 <= x < 10).
#     """
#     assert isinstance(node, ast.Compare)
#     ops = _find_to_ops(node)
#     return build_mutations(map(type, node.ops), ops)


# def _find_to_ops(node):
#     """Iterable of possible operators the node could be mutated to.
#     """
#     if _comparison_rhs_is_none(node):
#         ops = _rhs_is_none_ops
#     elif _comparison_rhs_is_integer(node):
#         ops = _rhs_is_integer_ops
#     else:
#         ops = _all_ops
# return ops
