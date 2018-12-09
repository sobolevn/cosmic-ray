"Implementation of the boolean replacement operators."

import parso.python.tree

from .keyword_replacer import KeywordReplacementOperator
from .operator import Operator


class ReplaceTrueWithFalse(KeywordReplacementOperator):
    """An that replaces True with False."""
    def __init__(self):
        super().__init__('True', 'False')


class ReplaceFalseWithTrue(KeywordReplacementOperator):
    """An that replaces False with True."""
    def __init__(self):
        super().__init__('False', 'True')


class ReplaceAndWithOr(KeywordReplacementOperator):
    """An operator that swaps 'and' with 'or'."""
    def __init__(self):
        super().__init__('and', 'or')


class ReplaceOrWithAnd(KeywordReplacementOperator):
    """An operator that swaps 'or' with 'and'."""
    def __init__(self):
        super().__init__('or', 'and')


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