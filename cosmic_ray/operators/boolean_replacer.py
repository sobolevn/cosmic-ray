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
    NODE_TYPES = (parso.python.tree.IfStmt,
                  parso.python.tree.WhileStmt,
                  parso.python.tree.AssertStmt)

    def mutation_count(self, node):
        if isinstance(node, self.NODE_TYPES):
            return 1
        elif isinstance(node, parso.python.tree.PythonNode) and node.type == 'test':
            # ternary conditional
            return 1
        return 0

    def mutate(self, node, index):
        assert index == 0

        if isinstance(node, self.NODE_TYPES):
            expr_node = node.children[1]
            mutated_code = ' not{}'.format(expr_node.get_code())
            mutated_node = parso.parse(mutated_code)
            node.children[1] = mutated_node

        else:
            assert node.type == 'test'
            expr_node = node.children[2]
            mutated_code = ' not{}'.format(expr_node.get_code())
            mutated_node = parso.parse(mutated_code)
            node.children[2] = mutated_node

        return node