"Implementation of the exception-replacement operator."

import builtins

from parso.python.tree import Name, PythonNode

from .operator import Operator


class CosmicRayTestingException(Exception):
    "A special exception we throw that nobody should be trying to catch."
    pass


# We inject this into builtins so we can easily replace other exceptions
# without necessitating the import of other modules.
setattr(builtins,
        CosmicRayTestingException.__name__,
        CosmicRayTestingException)


class ExceptionReplacer(Operator):
    """An operator that modifies exception handlers."""

    def mutation_count(self, node):
        if isinstance(node, PythonNode):
            if node.type == 'except_clause':
                return len(self._name_nodes(node))

        return 0

    def mutate(self, node, index):
        assert isinstance(node, PythonNode)
        assert node.type == 'except_clause'

        name_nodes = self._name_nodes(node)
        assert index < len(name_nodes)
        name_nodes[index].value = CosmicRayTestingException.__name__
        return node

    @staticmethod
    def _name_nodes(node):
        if isinstance(node.children[1], Name):
            return (node.children[1],)
        else:
            atom = node.children[1]
            test_list = atom.children[1]
            return test_list.children[::2]
