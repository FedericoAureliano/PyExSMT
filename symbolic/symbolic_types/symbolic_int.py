# Copyright: copyright.txt

from . symbolic_object import SymbolicObject, wrap

from pysmt.shortcuts import INT

class SymbolicInteger(SymbolicObject):
    def __init__(self, expr, name = "se"):
        SymbolicObject.__init__(self, expr, name, INT)

# now update the SymbolicInteger class for operations we
# will build symbolic terms for
    def __add__(self, other):
        other = wrap(other)
        if self.expr.get_type() != other.get_type():
            return False
        return SymbolicObject(self.expr + other)

    def __sub__(self, other):
        other = wrap(other)
        if self.expr.get_type() != other.get_type():
            return False
        return SymbolicObject(self.expr - other)

    def __mul__(self, other):
        other = wrap(other)
        if self.expr.get_type() != other.get_type():
            return False
        return SymbolicObject(self.expr * other)

    def __mod__(self, other):
        raise NotImplementedError("mod Not Implemented Yet!")

    def __div__(self, other):
        other = wrap(other)
        if self.expr.get_type() != other.get_type():
            return False
        return SymbolicObject(self.expr / other)

    def __and__(self, other):
        raise NotImplementedError("and Not Implemented Yet!")

    def __or__(self, other):
        raise NotImplementedError("or Not Implemented Yet!")

    def __xor__(self, other):
        raise NotImplementedError("xor Not Implemented Yet!")

    def __lshift__(self, other):
        raise NotImplementedError("lshift Not Implemented Yet!")

    def __rshift__(self, other):
        raise NotImplementedError("rshift Not Implemented Yet!")