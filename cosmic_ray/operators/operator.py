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


def _op_name(from_op_name, to_op_name):
    assert from_op_name or to_op_name, 'Cannot make replacement operator from None to None'

    if from_op_name is None:
        return 'Insert_{}'.format(to_op_name)
    elif to_op_name is None:
        return 'Delete_{}'.format(from_op_name)

    return '{}_{}'.format(from_op_name, to_op_name)


# TODO: Can we replace this with a class decorator?
def replacement_operator(from_op, from_op_name, to_op, to_op_name):
    """Class decorator for mutation operators that replace Python operators.

    This does a few things:

    - Sets the name of the class object based on the class declaration 
    - Makes the from-/to-operators available as class members.
    """
    def dec(cls):
        name = '{}_{}'.format(
            cls.__name__,
            _op_name(from_op_name, to_op_name))
        setattr(cls, '__name__', name)
        cls.from_op = from_op
        cls.to_op = to_op
        return cls
    return dec
