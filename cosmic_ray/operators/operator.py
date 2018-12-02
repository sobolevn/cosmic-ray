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

def _op_name(from_op, to_op):
    assert from_op or to_op, 'Cannot make replacement operator from None to None' 

    if from_op is None:
        return 'Insert_{}'.format(to_op.__name__)
    elif to_op is None:
        return 'Delete_{}'.format(from_op.__name__)

    return '{}_{}'.format(from_op.__name__, to_op.__name__)


class ReplacementOperatorMeta(type):
    """Metaclass for mutation operators that replace Python operators.

    This does a few things:

    - Sets the name of the class object based on the class declaration *and* the from-/to-operators.
    - Makes the from-/to-operators available as class members.
    - Adds `Operator` as a base class.
    """
    def __init__(cls, name, bases, namespace, from_op, to_op, **kwargs):
        super().__init__(name, bases, namespace, **kwargs)

    def __new__(cls, name, bases, namespace, from_op, to_op, **kwargs):
        name = '{}_{}'.format(
            name,
            _op_name(from_op, to_op))
        bases = bases + (Operator,)
        namespace['from_op'] = from_op
        namespace['to_op'] = to_op
        return super().__new__(cls, name, bases, namespace, **kwargs)
