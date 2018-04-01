# Copyright - see copyright.txt
from pyexsmt import pred_to_smt
from pysmt.shortcuts import *
from pyexsmt.symbolic_types.symbolic_object import SymbolicObject

class Predicate:
    """Predicate is one specific ``if'' encountered during the program execution.
       """
    def __init__(self, st, result):
        self.symtype = st
        self.result = result

    def __eq__(self, other):
        if isinstance(other, Predicate):
            res = self.result == other.result and self.symtype.symbolic_eq(other.symtype)
            return res
        else:
            return False

    def __hash__(self):
        return hash(self.symtype)

    def __str__(self):
        return "%s (%s)" % (repr(self.symtype), self.result)

    def __repr__(self):
        return self.__str__()

    def negate(self):
        """Negates the current predicate"""
        assert self.result is not None
        self.result = not self.result

    def AND(self, other):
        if isinstance(other, Predicate):
            if (self == other):
                return Predicate(self.symtype, self.result)
            symtype = SymbolicObject(And(pred_to_smt(self), pred_to_smt(other)))
        else:
            symtype = self.symtype
            result = self.result
        return Predicate(symtype, True)
