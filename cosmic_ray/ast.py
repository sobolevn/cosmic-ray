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


def get_ast(module_path, python_version):
    with module_path.open(mode='rt', encoding='utf-8') as handle:
        source = handle.read()

    return parso.parse(source, version=python_version)
