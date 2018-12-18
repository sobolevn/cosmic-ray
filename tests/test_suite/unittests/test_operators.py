"""Tests for the various mutation operators.
"""
import pytest

import parso

from cosmic_ray.operators.comparison_operator_replacement import *
from cosmic_ray.operators.unary_operator_replacement import *
from cosmic_ray.operators.binary_operator_replacement import *
from cosmic_ray.operators.boolean_replacer import ReplaceTrueWithFalse, ReplaceFalseWithTrue, ReplaceAndWithOr, ReplaceOrWithAnd, AddNot
from cosmic_ray.operators.break_continue import ReplaceBreakWithContinue, ReplaceContinueWithBreak
from cosmic_ray.operators.exception_replacer import ExceptionReplacer
from cosmic_ray.operators.number_replacer import NumberReplacer
from cosmic_ray.operators.remove_decorator import RemoveDecorator
from cosmic_ray.operators.zero_iteration_for_loop import ZeroIterationForLoop
from cosmic_ray.mutating import MutationVisitor


class Sample:
    def __init__(self, operator, from_code, to_code, index=0):
        self.operator = operator
        self.from_code = from_code
        self.to_code = to_code
        self.index = index


OPERATOR_SAMPLES = [
    Sample(*args) for args in (
        (ReplaceTrueWithFalse, 'True', 'False'),
        (ReplaceFalseWithTrue, 'False', 'True'),
        (ReplaceAndWithOr, 'if True and False: pass',
         'if True or False: pass'),
        (ReplaceOrWithAnd, 'if True or False: pass',
         'if True and False: pass'),
        (AddNot, 'if True or False: pass', 'if not True or False: pass'),
        (AddNot, 'A if B else C', 'A if not B else C'),
        (AddNot, 'assert isinstance(node, ast.Break)',
         'assert not isinstance(node, ast.Break)'),
        (AddNot, 'while True: pass', 'while not True: pass'),
        (ReplaceBreakWithContinue, 'while True: break',
         'while True: continue'),
        (ReplaceContinueWithBreak, 'while False: continue',
         'while False: break'),
        (NumberReplacer, 'x = 1', 'x = 2'),
        (NumberReplacer, 'x = 1', 'x = 0', 1),
        (NumberReplacer, 'x = 4.2', 'x = 5.2'),
        (NumberReplacer, 'x = 4.2', 'x = 3.2', 1),
        (NumberReplacer, 'x = 1j', 'x = (1+1j)'),
        (NumberReplacer, 'x = 1j', 'x = (-1+1j)', 1),
        (ReplaceComparisonOperator_Eq_IsNot, 'x == y', 'x is not y'),
        (ReplaceComparisonOperator_Gt_Lt, 'if x > y: pass', 'if x < y: pass'),
        (ReplaceComparisonOperator_Is_IsNot, 'if x is None: pass',
         'if x is not None: pass'),
        (ReplaceComparisonOperator_Gt_Eq, 'if x > 42: pass',
         'if x == 42: pass'),
        (ReplaceComparisonOperator_Gt_Eq, 'if x > 42 > 69: pass',
         'if x > 42 == 69: pass', 1),
        (ReplaceComparisonOperator_LtE_IsNot, 'if x <= 4 <= 5 <= 4.3: pass',
         'if x <= 4 <= 5 is not 4.3: pass', 2),
        (ReplaceBinaryOperator_Mul_Add, 'x * y', 'x + y'),
        (ReplaceBinaryOperator_Sub_Mod, 'x - y', 'x % y'),
        (ZeroIterationForLoop, 'for i in range(1,2): pass',
         'for i in []: pass'),
        (RemoveDecorator, '@foo\ndef bar(): pass', 'def bar(): pass'),
        (RemoveDecorator, '@first\n@second\ndef bar(): pass',
         '@second\ndef bar(): pass'),
        (RemoveDecorator, '@first\n@second\ndef bar(): pass',
         '@first\ndef bar(): pass', 1),
        (RemoveDecorator, '@first\n@second\n@third\ndef bar(): pass',
         '@first\n@third\ndef bar(): pass', 1),
        (ExceptionReplacer, 'try: raise OSError\nexcept OSError: pass',
         'try: raise OSError\nexcept CosmicRayTestingException: pass'),
        (ExceptionReplacer,
         'try: raise OSError\nexcept (OSError, ValueError): pass',
         'try: raise OSError\nexcept (OSError, CosmicRayTestingException): pass',
         1),
        (ExceptionReplacer,
         'try: raise OSError\nexcept (OSError, ValueError, KeyError): pass',
         'try: raise OSError\nexcept (OSError, CosmicRayTestingException, KeyError): pass',
         1),
        (ExceptionReplacer, 'try: pass\nexcept: pass',
         'try: pass\nexcept: pass'),
        (ReplaceUnaryOperator_USub_UAdd, 'x = -1', 'x = +1'),
        (ReplaceUnaryOperator_UAdd_USub, 'x = +1', 'x = -1'),
        (ReplaceUnaryOperator_Delete_Not, 'return not x', 'return  x'),
        (ReplaceUnaryOperator_Delete_USub, "x = -1", "x = 1"),
        (ReplaceUnaryOperator_USub_Not, "x = -1", "x = not 1"),

        # Make sure unary and binary op mutators don't pick up the wrong kinds of operators
        (ReplaceUnaryOperator_USub_UAdd, 'x + 1', 'x + 1'),
        (ReplaceBinaryOperator_Add_Mul, '+1', '+1'),
    )
]


@pytest.mark.parametrize('sample', OPERATOR_SAMPLES)
def test_mutation_changes_ast(sample, python_version):
    node = parso.parse(sample.from_code)
    visitor = MutationVisitor(sample.index, sample.operator(python_version))
    mutant = visitor.walk(node)

    assert mutant.get_code() == sample.to_code


@pytest.mark.parametrize('sample', OPERATOR_SAMPLES)
def test_no_mutation_leaves_ast_unchanged(sample, python_version):
    node = parso.parse(sample.from_code)
    visitor = MutationVisitor(-1, sample.operator(python_version))
    mutant = visitor.walk(node)

    assert mutant.get_code() == sample.from_code
