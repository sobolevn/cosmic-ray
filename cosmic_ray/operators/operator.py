"Implementation of operator base class."

from abc import ABC, abstractmethod


class Operator(ABC):
    """The mutation operator base class.

    Args:
        python_version: The version of Python to use when interpreting the code in `module_path`. 
            A string of the form "MAJOR.MINOR", e.g. "3.6" for Python 3.6.x.
    """

    def __init__(self, python_version):
        self._python_version = python_version

    @property
    def python_version(self):
        "Python major.minor version as a string."
        return self._python_version

    @abstractmethod
    def mutation_positions(self, node):
        """All positions where this operator can mutate `node`.

        An operator might be able to mutate a node in multiple ways, and this
        function should produce a position description for each of these
        mutations. Critically, if an operator can make multiple mutations to the
        same position, this should produce a position for each of these
        mutations (i.e. multiple identical positions).

        Returns: An iterable of `((start-line, start-col), (stop-line,
            stop-col))` tuples describing the locations where this operator will
            mutate `node`. 
        """
        pass

    @abstractmethod
    def mutate(self, node, index):
        """Mutate a node in an operator-specific manner.

        Return the new, mutated node. Return `None` if the node has
        been deleted. Return `node` if there is no mutation at all for
        some reason.
        """
        pass
