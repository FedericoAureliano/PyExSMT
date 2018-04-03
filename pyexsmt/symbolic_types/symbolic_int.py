# Copyright: copyright.txt

from pyexsmt.symbolic_types.symbolic_object import SymbolicObject, to_pysmt
from pyexsmt.symbolic_types.symbolic_object import create_shadow as ob_create_shadow

from pysmt.shortcuts import *

class SymbolicInteger(SymbolicObject):
    def __init__(self, expr, name = "se", shadow_expr = None):
        SymbolicObject.__init__(self, expr, name, INT, shadow_expr)


    def symbloic(self, symbolicExpr, name="se", ty=INT):
        if symbolicExpr is None:
            expr = Symbol(name, ty)
        else:
            #if the expression is a symbolic object, extract its shadow expression
            expr = to_pysmt(symbolicExpr, shadow=False)

        return SymbolicInteger(expr=expr, shadow_expr=self.shadow_expr);

    def shadow(self, shadowExpr, name="se", ty=INT):
        if shadowExpr is None:
            shadow_expr = Symbol(name, ty)
        else:
            #if the expression is a symbolic object, extract its shadow expression
            shadow_expr = to_pysmt(shadowExpr, shadow=True)

        return SymbolicInteger(expr=self.expr, shadow_expr=shadow_expr);

    #method convert self to a shadow symbolic object, make shadow the foreground value
    def to_shadow(self):
        return SymbolicInteger(expr=self.shadow_expr)


    ## LOGICAL OPERATORS
    def __and__(self, other):
        raise NotImplementedError("and is not implemented for %s!" % self.expr.get_type())

    def __or__(self, other):
        raise NotImplementedError("or is not implemented for %s!" % self.expr.get_type())

    ## ARITHMETIC OPERATORS
    def __add__(self, other):
        other_shadow = to_pysmt(other, shadow=True)
        other = to_pysmt(other)
        if self.expr.get_type() != other.get_type():
            raise TypeError("CANNOT '+' %s and %s" %(self.expr.get_type(), other.get_type()))
        return SymbolicInteger(self.expr + other, shadow_expr=(self.shadow_expr + other_shadow))

    def __sub__(self, other):
        other_shadow = to_pysmt(other, shadow=True)
        other = to_pysmt(other)
        if self.expr.get_type() != other.get_type():
            raise TypeError("CANNOT '-' %s and %s" %(self.expr.get_type(), other.get_type()))
        return SymbolicInteger(self.expr - other, shadow_expr=(self.shadow_expr - other_shadow))

    def __mul__(self, other):
        other_shadow = to_pysmt(other, shadow=True)
        other = to_pysmt(other)
        if self.expr.get_type() != other.get_type():
            raise TypeError("CANNOT '*' %s and %s" %(self.expr.get_type(), other.get_type()))
        return SymbolicInteger(self.expr * other, shadow_expr=(self.shadow_expr * other_shadow))

    def __mod__(self, other):
        other_shadow = to_pysmt(other, shadow=True)
        other = to_pysmt(other)
        if self.expr.get_type() != other.get_type() or self.expr.get_type() != INT:
            raise TypeError("CANNOT 'mod' %s and %s" %(self.expr.get_type(), other.get_type()))
        return SymbolicInteger(self.expr % other, shadow_expr=(self.shadow_expr % other_shadow))


    def __floordiv__(self, other):
        other_shadow = to_pysmt(other, shadow=True)
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

# method to create a shadow expression for INT type symbolic and shadow Integer
def create_shadow(symbolic_expression, shadow_expression):
    if isinstance(symbolic_expression, SymbolicInteger):
        expr = symbolic_expression.expr
    elif isinstance(symbolic_expression, int) or symbolic_expression is None :
        expr = to_pysmt(symbolic_expression)
    else:
        # if the input expression is not int, then use the genereic symbolic object
        return ob_create_shadow(symbolic_expression, shadow_expression)

    if isinstance(shadow_expression, SymbolicInteger):
        shadow_expr = shadow_expression.shadow_expr
    elif isinstance(shadow_expression, int) or shadow_expression is None:
        shadow_expr = to_pysmt(shadow_expression, shadow=True)
    else:
        # if the shadow expression is not int, then use the genereic symbolic object
        return ob_create_shadow(symbolic_expression, shadow_expression)

    return SymbolicInteger(expr=expr, shadow_expr=shadow_expr)