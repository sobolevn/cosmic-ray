"""Tests for the various mutation operators.
"""
import copy
import pytest

import parso

# from cosmic_ray.operators.comparison_operator_replacement import \
#     (ReplaceComparisonOperator_Gt_Lt,
#      ReplaceComparisonOperator_Is_IsNot,
#      ReplaceComparisonOperator_Gt_Eq)
# from cosmic_ray.operators.unary_operator_replacement import \
#     (ReplaceUnaryOperator_Delete_Not,
#      ReplaceUnaryOperator_USub_UAdd)
# from cosmic_ray.operators.binary_operator_replacement import \
#     (ReplaceBinaryOperator_Mult_Add,
#      ReplaceBinaryOperator_Sub_Mod)
# from cosmic_ray.counting import _CountingCore
from cosmic_ray.operators.boolean_replacer import ReplaceTrueFalse
#                                                    ReplaceAndWithOr,
#                                                    ReplaceOrWithAnd,
#                                                    AddNot)
# from cosmic_ray.operators.break_continue import (ReplaceBreakWithContinue,
#                                                  ReplaceContinueWithBreak)
# from cosmic_ray.operators.exception_replacer import ExceptionReplacer
# from cosmic_ray.operators.number_replacer import NumberReplacer
# from cosmic_ray.operators.remove_decorator import RemoveDecorator
# from cosmic_ray.operators.zero_iteration_loop import ZeroIterationLoop
from cosmic_ray.mutating import MutationVisitor


OPERATOR_SAMPLES = [
    (ReplaceTrueFalse, 'True'),
    # (ReplaceAndWithOr, 'if True and False: pass'),
    # (ReplaceOrWithAnd, 'if True or False: pass'),
    # (AddNot, 'if True or False: pass'),
    # (AddNot, 'A if B else C'),
    # (AddNot, 'assert isinstance(node, ast.Break)'),
    # (AddNot, 'while True: pass'),
    # (ReplaceBreakWithContinue, 'while True: break'),
    # (ReplaceContinueWithBreak, 'while False: continue'),
    # (NumberReplacer, 'x = 1'),
    # (ReplaceComparisonOperator_Gt_Lt, 'if x > y: pass'),
    # (ReplaceComparisonOperator_Is_IsNot, 'if x is None: pass'),
    # (ReplaceComparisonOperator_Gt_Eq, 'if x > 42: pass'),
    # (ReplaceUnaryOperator_Delete_Not, 'return not X'),
    # (ReplaceUnaryOperator_USub_UAdd, 'x = -1'),
    # (ReplaceBinaryOperator_Mult_Add, 'x * y'),
    # (ReplaceBinaryOperator_Sub_Mod, 'x - y'),
    # (ExceptionReplacer, 'try: raise OSError \nexcept OSError: pass'),
    # (ZeroIterationLoop, 'for i in range(1,2): pass'),
    # (RemoveDecorator, 'def wrapper(f): f.cosmic_ray=1; '
    #                   'return f\n@wrapper\ndef foo(): pass')
]


@pytest.mark.parametrize('operator,code', OPERATOR_SAMPLES)
def test_activation_record_created(operator, code):
    node = parso.parse(code)
    visitor = MutationVisitor(0, operator())

    assert visitor.activation_record is None

    visitor.walk(node)

    assert visitor.activation_record is not None


@pytest.mark.parametrize('operator,code', OPERATOR_SAMPLES)
def test_no_activation_record_created(operator, code):
    node = parso.parse(code)
    visitor = MutationVisitor(-1, operator())
    visitor.walk(node)
    assert visitor.activation_record is None


@pytest.mark.parametrize('operator,code', OPERATOR_SAMPLES)
def test_mutation_changes_ast(operator, code):
    node = parso.parse(code)
    visitor = MutationVisitor(0, operator())
    mutant = visitor.walk(node)

    assert mutant.get_code() != code


@pytest.mark.parametrize('operator,code', OPERATOR_SAMPLES)
def test_no_mutation_leaves_ast_unchanged(operator, code):
    node = parso.parse(code)
    visitor = MutationVisitor(-1, operator())
    mutant = visitor.walk(node)

    assert mutant.get_code() == code