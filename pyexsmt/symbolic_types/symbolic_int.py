# Copyright: copyright.txt

from pyexsmt.symbolic_types.symbolic_object import SymbolicObject, to_pysmt

from pysmt.shortcuts import *

class SymbolicInteger(SymbolicObject):
    def __init__(self, expr, name = "se", shadow_expr = None):
        SymbolicObject.__init__(self, expr, name, INT, shadow_expr)

    ## LOGICAL OPERATORS
    def __and__(self, other):
        raise NotImplementedError("and is not implemented for %s!" % self.expr.get_type())

    def __or__(self, other):
        raise NotImplementedError("or is not implemented for %s!" % self.expr.get_type())

    ## ARITHMETIC OPERATORS
    def __add__(self, other):
        other_shadow = to_pysmt(other)
        other = to_pysmt(other)
        if self.expr.get_type() != other.get_type():
            raise TypeError("CANNOT '+' %s and %s" %(self.expr.get_type(), other.get_type()))
        return SymbolicInteger(self.expr + other, shadow_expr=(self.shadow_expr + other_shadow))

    def __sub__(self, other):
        other_shadow = to_pysmt(other)
        other = to_pysmt(other)
        if self.expr.get_type() != other.get_type():
            raise TypeError("CANNOT '-' %s and %s" %(self.expr.get_type(), other.get_type()))
        return SymbolicInteger(self.expr - other, shadow_expr=(self.shadow_expr - other_shadow))

    def __mul__(self, other):
        other_shadow = to_pysmt(other)
        other = to_pysmt(other)
        if self.expr.get_type() != other.get_type():
            raise TypeError("CANNOT '*' %s and %s" %(self.expr.get_type(), other.get_type()))
        return SymbolicInteger(self.expr * other, shadow_expr=(self.shadow_expr * other_shadow))

    def __mod__(self, other):
        other_shadow = to_pysmt(other)
        other = to_pysmt(other)
        if self.expr.get_type() != other.get_type() or self.expr.get_type() != INT:
            raise TypeError("CANNOT 'mod' %s and %s" %(self.expr.get_type(), other.get_type()))
        return SymbolicInteger(self.expr % other, shadow_expr=(self.shadow_expr % other_shadow))


    def __floordiv__(self, other):
        other_shadow = to_pysmt(other)
        other = to_pysmt(other)
        if self.expr.get_type() != other.get_type() or self.expr.get_type() != INT:
            raise TypeError("CANNOT '//' %s and %s" %(self.expr.get_type(), other.get_type()))
        return SymbolicInteger(self.expr // other, shadow_expr=(self.shadow_expr // other_shadow))

    ## UNARY OPERATORS
    def __neg__ (self):
        return SymbolicInteger(Int(0) - self.expr, shadow_expr=(Int(0) - self.shadow_expr))

    def __pos__ (self):
        return self

    def __abs__ (self):
        return SymbolicInteger(Ite(self.expr < 0, -self.expr, self.expr), shadow_expr=Ite(self.shadow_expr< 0, -self.shadow_expr, self.shadow_expr))

    ## REVERSE OPERATORS
    def __radd__ (self, other):
        return self.__add__(other)
    
    def __rmul__ (self, other):
        return self.__mul__(other)

    def __rsub__(self, other):
        return (-self).__add__(other)