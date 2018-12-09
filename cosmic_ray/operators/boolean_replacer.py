"Implementation of the boolean replacement operators."

import ast
import sys

import parso.python.tree

from .operator import Operator


class ReplaceTrueFalse(Operator):
    """An operator that modifies True/False constants."""

    def mutation_count(self, node):
        if isinstance(node, parso.python.tree.Keyword):
            if node.value == 'True' or node.value == 'False':
                return 1

        return 0

    def mutate(self, node, index):
        node.value = 'True' if node.value == 'False' else 'False'
        return node


class ReplaceAndWithOr(Operator):
    """An operator that swaps 'and' with 'or'."""

    def mutation_count(self, node):
        if isinstance(node, parso.python.tree.Keyword):
            if node.value == 'and':
                return 1
        return 0

    def mutate(self, node, idx):
        assert idx == 0
        assert node.value == 'and'
        node.value = 'or'
        return node


class ReplaceOrWithAnd(Operator):
    """An operator that swaps 'or' with 'and'."""
    def mutation_count(self, node):
        if isinstance(node, parso.python.tree.Keyword):
            if node.value == 'or':
                return 1
        return 0

    def mutate(self, node, idx):
        assert idx == 0
        assert node.value == 'or'
        node.value = 'and'
        return node


class AddNot(Operator):
    """
        An operator that adds the 'not' keyword to boolean expressions.

        NOTE: 'not' as unary operator is mutated in
         `unary_operator_replacement.py`, including deletion of the same
         operator.
    """

    def visit_If(self, node):  # noqa # pylint: disable=invalid-name
        "Visit an 'if' node."
        return self.visit_mutation_site(node)

    def visit_IfExp(self, node):  # noqa # pylint: disable=invalid-name
        "Visit an 'if' expression node."
        return self.visit_mutation_site(node)

    def visit_Assert(self, node):  # noqa # pylint: disable=invalid-name
        "Visit an 'assert' node."
        return self.visit_mutation_site(node)

    def visit_While(self, node):  # noqa # pylint: disable=invalid-name
        "Visit a 'while' node."
        return self.visit_mutation_site(node)

    def mutate(self, node, _):
        """
        Add the 'not' keyword.

        Note: this will negate the entire if condition.
        """
        if hasattr(node, 'test'):
            node.test = ast.UnaryOp(op=ast.Not(), operand=node.test)
            return node
