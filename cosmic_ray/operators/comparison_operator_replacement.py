"""This module contains mutation operators which replace one
comparison operator with another.
"""
import itertools

import parso.python.tree

from .operator import Operator


# Notes: look for a parso Node with 'node.type == "comparison"'. The second
# child might be a 'comp_op', or it might be an Operator node. These will
# contain the elements of the operator that we need to work with.

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

def set_name(from_op_name, to_op_name):
    def dec(cls):
        name = '{}_{}_{}'.format(
            cls.__name__,
            from_op_name, 
            to_op_name)
        setattr(cls, '__name__', name)
        return cls
    return dec


def _create_operator(from_op, from_op_name, to_op, to_op_name):
    @set_name(from_op_name, to_op_name)
    class ReplaceComparisonOperator(Operator):
        def mutation_count(self, node):
            if node.type == 'operator':
                if node.value == self.from_op:
                    return 1
            elif node.type == 'comp_op':
                if node.value == self.from_op:
                    return 1
            return 0

        def mutate(self, node, index):
            code = 'x {} y'.format(self.to_op)

            # TODO: this is technically wrong because we don't set the correct
            # start/end_pos. Does this matter?
            return parso.parse(code).children[0].children[1]

    ReplaceComparisonOperator.from_op = from_op
    ReplaceComparisonOperator.to_op = to_op

    return ReplaceComparisonOperator

# Build all of the binary replacement operators
_OPERATORS = tuple(
    _create_operator(from_op, from_name, to_op, to_name)
    for (from_op, from_name), (to_op, to_name) 
    in itertools.permutations(_OPERATOR_DESCRIPTIONS, 2))

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