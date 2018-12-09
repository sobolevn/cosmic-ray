"""Tests for the various mutation operators.
"""
import copy
import pytest

import parso

from cosmic_ray.operators.comparison_operator_replacement import *
# from cosmic_ray.operators.unary_operator_replacement import \
#     (ReplaceUnaryOperator_Delete_Not,
#      ReplaceUnaryOperator_USub_UAdd)
from cosmic_ray.operators.binary_operator_replacement import *  
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


class Sample:
    def __init__(self, operator, from_code, to_code, index=0):
        self.operator = operator
        self.from_code = from_code
        self.to_code = to_code
        self.index = index


OPERATOR_SAMPLES = [
    Sample(*args)
    for args in (

        (ReplaceTrueFalse, 'True', 'False'),
        # (ReplaceAndWithOr, 'if True and False: pass'),
        # (ReplaceOrWithAnd, 'if True or False: pass'),
        # (AddNot, 'if True or False: pass'),
        # (AddNot, 'A if B else C'),
        # (AddNot, 'assert isinstance(node, ast.Break)'),
        # (AddNot, 'while True: pass'),
        # (ReplaceBreakWithContinue, 'while True: break'),
        # (ReplaceContinueWithBreak, 'while False: continue'),
        # (NumberReplacer, 'x = 1'),
        (ReplaceComparisonOperator_Eq_IsNot, 'x == y', 'x is not y'),
        (ReplaceComparisonOperator_Gt_Lt, 'if x > y: pass', 'if x < y: pass'),
        (ReplaceComparisonOperator_Is_IsNot, 'if x is None: pass', 'if x is not None: pass'),
        (ReplaceComparisonOperator_Gt_Eq, 'if x > 42: pass', 'if x == 42: pass'),
        (ReplaceComparisonOperator_Gt_Eq, 'if x > 42 > 69: pass', 'if x > 42 == 69: pass', 1),
        (ReplaceComparisonOperator_LtE_IsNot, 'if x <= 4 <= 5 <= 4.3: pass', 'if x <= 4 <= 5 is not 4.3: pass', 2),
        # (ReplaceUnaryOperator_Delete_Not, 'return not X'),
        # (ReplaceUnaryOperator_USub_UAdd, 'x = -1'),
        (ReplaceBinaryOperator_Mul_Add, 'x * y', 'x + y'),
        (ReplaceBinaryOperator_Sub_Mod, 'x - y', 'x % y'),
        # (ExceptionReplacer, 'try: raise OSError \nexcept OSError: pass'),
        # (ZeroIterationLoop, 'for i in range(1,2): pass'),
        # (RemoveDecorator, 'def wrapper(f): f.cosmic_ray=1; '
        #                   'return f\n@wrapper\ndef foo(): pass')
    )
]


@pytest.mark.parametrize('sample', OPERATOR_SAMPLES)
def test_activation_record_created(sample):
    node = parso.parse(sample.from_code)
    visitor = MutationVisitor(0, sample.operator())

    assert visitor.activation_record is None

    visitor.walk(node)

    assert visitor.activation_record is not None


@pytest.mark.parametrize('sample', OPERATOR_SAMPLES)
def test_no_activation_record_created(sample):
    node = parso.parse(sample.from_code)
    visitor = MutationVisitor(-1, sample.operator())
    visitor.walk(node)
    assert visitor.activation_record is None


@pytest.mark.parametrize('sample', OPERATOR_SAMPLES)
def test_mutation_changes_ast(sample):
    node = parso.parse(sample.from_code)
    visitor = MutationVisitor(sample.index, sample.operator())
    mutant = visitor.walk(node)

    assert mutant.get_code() == sample.to_code


@pytest.mark.parametrize('sample', OPERATOR_SAMPLES)
def test_no_mutation_leaves_ast_unchanged(sample):
    node = parso.parse(sample.from_code)
    visitor = MutationVisitor(-1, sample.operator())
    mutant = visitor.walk(node)

    assert mutant.get_code() == sample.from_code
