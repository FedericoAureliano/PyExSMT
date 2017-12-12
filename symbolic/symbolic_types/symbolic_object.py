# Copyright: see copyright.txt

import logging

from pysmt.shortcuts import *

# the ABSTRACT base class for representing any expression that depends on a symbolic input
# it also tracks the corresponding concrete value for the expression (aka concolic execution)

class SymbolicObject(object):
    def __init__(self, expr, name = "se", ty=INT):
        if expr is None:
            self.expr = Symbol(name, ty)
        else:
            self.expr = expr
        self.val = 0

    # This is set up by the concolic engine to link __bool__ to PathConstraint
    SI = None
    # This is set up by the concolic engine to link the solver to the variables  
    SOLVER = None

    # this is a critical interception point: the __bool__
    # method is called whenever a predicate is evaluated in
    # Python execution (if, while, and, or). This allows us
    # to capture the path condition
    def __bool__(self):
        ret = self.get_concr_value()
        if ret == FALSE() or ret == 0:
            ret = False
        else:
            ret = True

        if SymbolicObject.SI != None:
            SymbolicObject.SI.whichBranch(ret, self)
        
        return ret

    def get_concr_value(self):
        if SymbolicObject.SOLVER is None:
            raise ValueError("MUST SPECIFY SOLVER")
        if not SymbolicObject.SOLVER.last_result:
            raise ValueError("SOLVER MUST HAVE A MODEL")
        val = SymbolicObject.SOLVER.get_py_value(self.expr)
        logging.debug("%s := %s" %(self.__repr__(), val))
        return val

    def get_vars(self):
        return self.expr.get_free_variables()

    def symbolicEq(self, other):
        if not isinstance(other,SymbolicObject):
            ret = False
        ret = self.expr.__repr__() == other.expr.__repr__()
        logging.debug("Checking equality of %s and %s: result is %s" %(self, other, ret))
        return ret

    def __hash__(self):
        return hash(self.get_concr_value())

    def __str__(self):
        return str(self.get_concr_value())

    def __repr__(self):
        return self.expr.serialize()


    ## COMPARISON OPERATORS
    def __eq__(self, other):
        #TODO: what if self is not symbolic and other is?
        other = wrap(other)
        if self.expr.get_type() != other.get_type():
            return False
        return SymbolicObject(Equals(self.expr, other))

    def __ne__(self, other):
        other = wrap(other)
        if self.expr.get_type() != other.get_type():
            return False
        return SymbolicObject(NotEquals(self.expr, other))

    def __lt__(self, other):
        other = wrap(other)
        if self.expr.get_type() != other.get_type():
            return False
        return SymbolicObject(LT(self.expr, other))

    def __le__(self, other):
        other = wrap(other)
        if self.expr.get_type() != other.get_type():
            return False
        return SymbolicObject(LE(self.expr, other))

    def __gt__(self, other):
        other = wrap(other)
        if self.expr.get_type() != other.get_type():
            return False
        return SymbolicObject(GT(self.expr, other))

    def __ge__(self, other):
        other = wrap(other)
        if self.expr.get_type() != other.get_type():
            return False
        return SymbolicObject(GE(self.expr, other))

    ## LOGICAL OPERATORS
    def __and__(self, other):
        other = wrap(other)
        if self.expr.get_type() != other.get_type():
            raise TypeError("CANNOT AND %s and %s" %(self.expr.get_type(), other.get_type()))
        return SymbolicObject(And(self.expr, other))

    def __or__(self, other):
        other = wrap(other)
        if self.expr.get_type() != other.get_type():
            raise TypeError("CANNOT OR %s and %s" %(self.expr.get_type(), other.get_type()))
        return SymbolicObject(Or(self.expr, other))

    ## ARITHMETIC OPERATORS
    def __add__(self, other):
        raise NotImplementedError("add is not implemented for %s!" % self.expr.get_type())

    def __sub__(self, other):
        raise NotImplementedError("sub is not implemented for %s!" % self.expr.get_type())

    def __mul__(self, other):
        raise NotImplementedError("mul is not implemented for %s!" % self.expr.get_type())

    def __mod__(self, other):
        raise NotImplementedError("mod is not implemented for %s!" % self.expr.get_type())

    def __div__(self, other):
        raise NotImplementedError("div is not implemented for %s!" % self.expr.get_type())

    def __floordiv__(self, other):
        raise NotImplementedError("floordiv is not implemented for %s!" % self.expr.get_type())

    def __truediv__(self, other):
        raise NotImplementedError("truediv is not implemented for %s!" % self.expr.get_type())

    def __divmod__(self, other):
        raise NotImplementedError("divmod is not implemented for %s!" % self.expr.get_type())

    def __pow__(self, other):
        raise NotImplementedError("pow is not implemented for %s!" % self.expr.get_type())

    def __xor__(self, other):
        raise NotImplementedError("xor is not implemented for %s!" % self.expr.get_type())

    def __lshift__(self, other):
        raise NotImplementedError("lshift is not implemented for %s!" % self.expr.get_type())

    def __rshift__(self, other):
        raise NotImplementedError("rshift is not implemented for %s!" % self.expr.get_type())

    ## REVERSE OPERATORS
    def __radd__ (self, other):
        return self.__add__(other)
    
    def __rsub__ (self, other):
        raise NotImplementedError("rsub is not implemented for %s!" % self.expr.get_type())
    
    def __rmul__ (self, other):
        return self.__mul__(other)
    
    def __rdiv__ (self, other):
        raise NotImplementedError("rdiv is not implemented for %s!" % self.expr.get_type())
    
    def __rfloordiv__ (self, other):
        raise NotImplementedError("rfloordiv is not implemented for %s!" % self.expr.get_type())
    
    def __rtruediv__ (self, other):
        raise NotImplementedError("rtruediv is not implemented for %s!" % self.expr.get_type())
    
    def __rmod__ (self, other):
        raise NotImplementedError("rmod is not implemented for %s!" % self.expr.get_type())
    
    def __rdivmod__ (self, other):
        raise NotImplementedError("rdivmod is not implemented for %s!" % self.expr.get_type())
    
    def __rpow__ (self, other):
        raise NotImplementedError("rpow is not implemented for %s!" % self.expr.get_type())
    
    def __rlshift__ (self, other):
        raise NotImplementedError("rlshift is not implemented for %s!" % self.expr.get_type())
    
    def __rrshift__ (self, other):
        raise NotImplementedError("rrshift is not implemented for %s!" % self.expr.get_type())
    
    def __rand__ (self, other):
        return self.__and__(other)
    
    def __rxor__ (self, other):
        raise NotImplementedError("rxor is not implemented for %s!" % self.expr.get_type())
    
    def __ror__ (self, other):
        return self.__or__(other)

def wrap(val):
    if isinstance(val, SymbolicObject):
        return val.expr
    elif isinstance(val, int):
        return Int(val)
    else:
        raise NotImplementedError("Only integers supported at the moment.")
