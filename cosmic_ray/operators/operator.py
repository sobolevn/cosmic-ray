"Implementation of operator base class."

from abc import ABC, abstractmethod


class Operator(ABC):
    @abstractmethod
    def mutation_count(self, node):
        """Get the number of mutation this operator can perform at this site.
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
