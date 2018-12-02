from abc import ABC, abstractmethod

import parso.tree


class Visitor(ABC):
    """AST visitor for parso trees.
    """

    def walk(self, node):
        node = self.visit(node)

        if node is None:
            return None

        if isinstance(node, parso.tree.BaseNode):
            walked = map(self.walk, node.children)
            node.children = tuple(child for child in walked if child is not None)

        return node

    @abstractmethod
    def visit(self, node):
        pass 


class OperatorVisitor(Visitor):
    """A visitor that invokes uses and `Operator` to determine when to do something special.

    Whenever the `Operator` reports that it can mutate a node (via its `mutation_count` method), this calls `activate` on the visitor.
    """

    def __init__(self, operator):
        self._operator = operator

    @property
    def operator(self):
        "The operator this visitor is using."
        return self._operator

    def visit(self, node):
        count = self.operator.mutation_count(node)
        if count > 0:
            return self.activate(node, count)
        else:
            return node

    @abstractmethod
    def activate(self, node, count):
        pass


