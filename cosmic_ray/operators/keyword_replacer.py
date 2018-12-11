from parso.python.tree import Keyword

from .operator import Operator


class KeywordReplacementOperator(Operator):
    """A base class for operators that replace one keyword with another
    """
    def __init__(self, from_keyword, to_keyword):
        if from_keyword == to_keyword:
            raise ValueError('from and to keywords must be different')

        self._from = from_keyword
        self._to = to_keyword

    def mutation_positions(self, node):
        if isinstance(node, Keyword):
            if node.value == self._from:
                yield (node.start_pos, node.end_pos)

    def mutate(self, node, index):
        assert isinstance(node, Keyword)
        assert node.value == self._from

        node.value = self._to
        return node


