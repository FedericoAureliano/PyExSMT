from pyexsmt.symbolic_types.symbolic_object import SymbolicObject, to_pysmt
from pysmt.shortcuts import *

class DifferenceExpression(object):

    SHADOW_LEADING = False

    def __init__(self, origin_expr=None, shadow_expr=None):
        self.origin_expr = origin_expr
        self.shadow_expr = shadow_expr

    def check_to_merge(self):
        mismatch = self.origin_expr != self.shadow_expr
        if isinstance(mismatch, SymbolicObject):
            mismatch = is_sat(to_pysmt(mismatch))
        if (mismatch):
            return self
        else:
            return self.origin_expr

    def get_origin(self):
        return self.origin_expr

    def get_shadow(self):
        return self.shadow_expr

    def __bool__(self):

       is_origin_symbolic = isinstance(self.origin_expr, SymbolicObject)
       is_shadow_symbolic = isinstance(self.shadow_expr, SymbolicObject)

       #case 1, both of expressions are not symbolic, then get return value directly without perform branch forking
       if (not is_origin_symbolic) and (not is_shadow_symbolic):
           ret_origin = self.origin_expr.__bool__()
           ret_shadow = self.shadow_expr.__bool__()
           path_div = not (ret_origin == ret_shadow)
           if (path_div):
               SymbolicObject.SI.diverge = True

       #case 2, both of the expressions are symbolic, then we need to perform 4 way forking
       elif (is_origin_symbolic or is_shadow_symbolic):
           ret_origin , ret_shadow = None , None
           ret_origin_result , ret_shadow_result = None,None


           if is_origin_symbolic:
               ret_origin_symbolic = self.origin_expr.to_boolean()
               ret_origin_result = ret_origin_symbolic.get_concr_value()
               ret_origin = ret_origin_result
           else:
               ret_origin =self.origin_expr.__bool__()

           if is_shadow_symbolic:
               ret_shadow_symbolic = self.shadow_expr.to_boolean()
               ret_shadow_result = ret_shadow_symbolic.get_concr_value()
               ret_shadow = ret_shadow_result
           else:
               ret_shadow = self.shadow_expr.__bool__()

           if (ret_origin_result is None):
               ret_origin_result = ret_shadow_result
               ret_origin_symbolic = ret_shadow_symbolic

           if (ret_shadow_result is None):
               ret_shadow_result = ret_origin_result
               ret_shadow_symbolic = ret_origin_symbolic


           if SymbolicObject.SI is not None:
               if DifferenceExpression.SHADOW_LEADING:
                   SymbolicObject.SI.which_branch(ret_shadow_result, ret_shadow_symbolic, ret_origin_result, ret_origin_symbolic, shadowLeadding=True)
               else:
                   SymbolicObject.SI.which_branch(ret_origin_result, ret_origin_symbolic, ret_shadow_result, ret_shadow_symbolic)



       if DifferenceExpression.SHADOW_LEADING:
           return ret_shadow
       else:
           return ret_origin


    def __hash__(self):
        return self.origin_expr.__hash__() + self.shadow_expr.__hash__()

    def __str__(self):
        return str(self.origin_expr.__str__() + "," +self.shadow_expr.__str__())

    def __repr__(self):
        return str(self.origin_expr.__repr__() + self.shadow_expr.__repr__())


    ## COMPARISON OPERATORS
    def __eq__(self, other):
        if isinstance(other, DifferenceExpression):
            ret_val = DifferenceExpression(self.origin_expr == other.origin_expr, self.shadow_expr == other.shadow_expr)
        else:
            ret_val=  DifferenceExpression(self.origin_expr == other, self.shadow_expr == other)

        return ret_val

    def __ne__(self, other):
        if isinstance(other, DifferenceExpression):
            ret_val = DifferenceExpression(self.origin_expr.__ne__(other.origin_expr), self.shadow_expr.__ne__(other.shadow_expr))
        else:
            ret_val = DifferenceExpression(self.origin_expr.__ne__(other), self.shadow_expr.__ne__(other))

        return ret_val

    def __lt__(self, other):
        if isinstance(other, DifferenceExpression):
            ret_val = DifferenceExpression(self.origin_expr.__lt__(other.origin_expr), self.shadow_expr.__lt__(other.shadow_expr))
        else:
            ret_val = DifferenceExpression(self.origin_expr.__lt__(other), self.shadow_expr.__lt__(other))

        return ret_val

    def __le__(self, other):
        if isinstance(other, DifferenceExpression):
            ret_val = DifferenceExpression(self.origin_expr.__le__(other.origin_expr), self.shadow_expr.__le__(other.shadow_expr))
        else:
            ret_val = DifferenceExpression(self.origin_expr.__le__(other), self.shadow_expr.__le__(other))

        return ret_val

    def __gt__(self, other):
        if isinstance(other, DifferenceExpression):
            ret_val = DifferenceExpression(self.origin_expr.__gt__(other.origin_expr), self.shadow_expr.__gt__(other.shadow_expr))
        else:
            ret_val = DifferenceExpression(self.origin_expr.__gt__(other), self.shadow_expr.__gt__(other))

        return ret_val

    def __ge__(self, other):
        if isinstance(other, DifferenceExpression):
            ret_val = DifferenceExpression(self.origin_expr.__ge__(other.origin_expr), self.shadow_expr.__ge__(other.shadow_expr))
        else:
            ret_val = DifferenceExpression(self.origin_expr.__ge__(other), self.shadow_expr.__ge__(other))

        return ret_val

    ## LOGICAL OPERATORS
    def __and__(self, other):
        if isinstance(other, DifferenceExpression):
            ret_val = DifferenceExpression(self.origin_expr.__and__(other.origin_expr), self.shadow_expr.__and__(other.shadow_expr))
        else:
            ret_val = DifferenceExpression(self.origin_expr.__and__(other), self.shadow_expr.__and__(other))

        return ret_val

    def __or__(self, other):
        if isinstance(other, DifferenceExpression):
            ret_val = DifferenceExpression(self.origin_expr.__or__(other.origin_expr), self.shadow_expr.__or__(other.shadow_expr))
        else:
            ret_val = DifferenceExpression(self.origin_expr.__or__(other), self.shadow_expr.__or__(other))

        return ret_val

    ## ARITHMETIC OPERATORS
    def __add__(self, other):
        if isinstance(other, DifferenceExpression):
            ret_val = DifferenceExpression(self.origin_expr + (other.origin_expr), self.shadow_expr + (other.shadow_expr))
        else:
            ret_val = DifferenceExpression(self.origin_expr + (other), self.shadow_expr + (other))

        return ret_val

    def __sub__(self, other):
        if isinstance(other, DifferenceExpression):
            ret_val = DifferenceExpression(self.origin_expr - (other.origin_expr), self.shadow_expr- (other.shadow_expr))
        else:
            ret_val = DifferenceExpression(self.origin_expr - (other), self.shadow_expr - (other))

        return ret_val

    def __mul__(self, other):
        if isinstance(other, DifferenceExpression):
            ret_val = DifferenceExpression(self.origin_expr * (other.origin_expr), self.shadow_expr * (other.shadow_expr))
        else:
            ret_val = DifferenceExpression(self.origin_expr * (other), self.shadow_expr * (other))

        return ret_val

    def __mod__(self, other):
        if isinstance(other, DifferenceExpression):
            ret_val = DifferenceExpression(self.origin_expr.__mod__(other.origin_expr), self.shadow_expr.__mod__(other.shadow_expr))
        else:
            ret_val = DifferenceExpression(self.origin_expr.__mod__(other), self.shadow_expr.__mod__(other))

        return ret_val

    def __floordiv__(self, other):
        if isinstance(other, DifferenceExpression):
            ret_val = DifferenceExpression(self.origin_expr.__floordiv__(other.origin_expr), self.shadow_expr.__floordiv__(other.shadow_expr))
        else:
            ret_val = DifferenceExpression(self.origin_expr.__floordiv__(other), self.shadow_expr.__floordiv__(other))

        return ret_val


    ## UNARY OPERATORS
    def __neg__(self):
        ret_val = DifferenceExpression(self.origin_expr.__neg__(), self.shadow_expr.__neg__())
        return ret_val

    def __pos__(self):
        ret_val = DifferenceExpression(self.origin_expr.__pos__(), self.shadow_expr.__pos__())
        return ret_val

    def __abs__(self):
        ret_val = DifferenceExpression(self.origin_expr.__abs__(), self.shadow_expr.__abs__())
        return ret_val

    ## REVERSE OPERATORS
    def __radd__(self, other):
        return self.__add__(other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __rsub__(self, other):
        return (-self).__add__(other)


    def __div__(self, other):
        if isinstance(other, DifferenceExpression):
            ret_val = DifferenceExpression(self.origin_expr.__div__(other.origin_expr), self.shadow_expr.__div__(other.shadow_expr))
        else:
            ret_val = DifferenceExpression(self.origin_expr.__div__(other), self.shadow_expr.__div__(other))

        return ret_val

    def __truediv__(self, other):
        if isinstance(other, DifferenceExpression):
            ret_val = DifferenceExpression(self.origin_expr.__truediv__(other.origin_expr), self.shadow_expr.__truediv__(other.shadow_expr))
        else:
            ret_val = DifferenceExpression(self.origin_expr.__truediv__(other), self.shadow_expr.__truediv__(other))

        return ret_val

    def __divmod__(self, other):
        if isinstance(other, DifferenceExpression):
            ret_val = DifferenceExpression(self.origin_expr.__divmod__(other.origin_expr), self.shadow_expr.__divmod__(other.shadow_expr))
        else:
            ret_val = DifferenceExpression(self.origin_expr.__divmod__(other), self.shadow_expr.__divmod__(other))

        return ret_val

    def __pow__(self, other):
        if isinstance(other, DifferenceExpression):
            ret_val = DifferenceExpression(self.origin_expr.__pow__(other.origin_expr), self.shadow_expr.__pow__(other.shadow_expr))
        else:
            ret_val = DifferenceExpression(self.origin_expr.__pow__(other), self.shadow_expr.__pow__(other))

        return ret_val

    def __xor__(self, other):
        if isinstance(other, DifferenceExpression):
            ret_val = DifferenceExpression(self.origin_expr.__xor__(other.origin_expr), self.shadow_expr.__xor__(other.shadow_expr))
        else:
            ret_val = DifferenceExpression(self.origin_expr.__xor__(other), self.shadow_expr.__xor__(other))

        return ret_val


    def __lshift__(self, other):
        if isinstance(other, DifferenceExpression):
            ret_val = DifferenceExpression(self.origin_expr.__lshift__(other.origin_expr), self.shadow_expr.__lshift__(other.shadow_expr))
        else:
            ret_val = DifferenceExpression(self.origin_expr.__lshift__(other), self.shadow_expr.__lshift__(other))

        return ret_val

    def __rshift__(self, other):
        if isinstance(other, DifferenceExpression):
            ret_val = DifferenceExpression(self.origin_expr.__rshift__(other.origin_expr), self.shadow_expr.__rshift__(other.shadow_expr))
        else:
            ret_val = DifferenceExpression(self.origin_expr.__rshift__(other), self.shadow_expr.__rshift__(other))

        return ret_val

    def __rdiv__(self, other):
        if isinstance(other, DifferenceExpression):
            ret_val = DifferenceExpression(self.origin_expr.__rdiv__(other.origin_expr), self.shadow_expr.__rdiv__(other.shadow_expr))
        else:
            ret_val = DifferenceExpression(self.origin_expr.__rdiv__(other), self.shadow_expr.__rdiv__(other))

        return ret_val

    def __rfloordiv__(self, other):
        if isinstance(other, DifferenceExpression):
            ret_val = DifferenceExpression(self.origin_expr.__rfloordiv__(other.origin_expr), self.shadow_expr.__rfloordiv__(other.shadow_expr))
        else:
            ret_val = DifferenceExpression(self.origin_expr.__rfloordiv__(other), self.shadow_expr.__rfloordiv__(other))

        return ret_val

    def __rtruediv__(self, other):
        if isinstance(other, DifferenceExpression):
            ret_val = DifferenceExpression(self.origin_expr.__rtruediv__(other.origin_expr), self.shadow_expr.__rtruediv__(other.shadow_expr))
        else:
            ret_val = DifferenceExpression(self.origin_expr.__rtruediv__(other), self.shadow_expr.__rtruediv__(other))

        return ret_val

    def __rmod__(self, other):
        if isinstance(other, DifferenceExpression):
            ret_val = DifferenceExpression(self.origin_expr.__rmod__(other.origin_expr), self.shadow_expr.__rmod__(other.shadow_expr))
        else:
            ret_val = DifferenceExpression(self.origin_expr.__rmod__(other), self.shadow_expr.__rmod__(other))

        return ret_val

    def __rdivmod__(self, other):
        if isinstance(other, DifferenceExpression):
            ret_val = DifferenceExpression(self.origin_expr.__rdivmod__(other.origin_expr), self.shadow_expr.__rdivmod__(other.shadow_expr))
        else:
            ret_val = DifferenceExpression(self.origin_expr.__rdivmod__(other), self.shadow_expr.__rdivmod__(other))

        return ret_val

    def __rpow__(self, other):
        if isinstance(other, DifferenceExpression):
            ret_val = DifferenceExpression(self.origin_expr.__rpow__(other.origin_expr), self.shadow_expr.__rpow__(other.shadow_expr))
        else:
            ret_val = DifferenceExpression(self.origin_expr.__rpow__(other), self.shadow_expr.__rpow__(other))

        return ret_val

    def __rlshift__(self, other):
        if isinstance(other, DifferenceExpression):
            ret_val = DifferenceExpression(self.origin_expr.__rlshift__(other.origin_expr), self.shadow_expr.__rlshift__(other.shadow_expr))
        else:
            ret_val = DifferenceExpression(self.origin_expr.__rlshift__(other), self.shadow_expr.__rlshift__(other))

        return ret_val

    def __rrshift__(self, other):
        if isinstance(other, DifferenceExpression):
            ret_val = DifferenceExpression(self.origin_expr.__rrshift__(other.origin_expr), self.shadow_expr.__rrshift__(other.shadow_expr))
        else:
            ret_val = DifferenceExpression(self.origin_expr.__rrshift__(other), self.shadow_expr.__rrshift__(other))

        return ret_val

    def __rand__(self, other):
        if isinstance(other, DifferenceExpression):
            ret_val = DifferenceExpression(self.origin_expr.__rand__(other.origin_expr), self.shadow_expr.__rand__(other.shadow_expr))
        else:
            ret_val = DifferenceExpression(self.origin_expr.__rand__(other), self.shadow_expr.__rand__(other))

        return ret_val

    def __rxor__(self, other):
        if isinstance(other, DifferenceExpression):
            ret_val = DifferenceExpression(self.origin_expr.__rxor__(other.origin_expr), self.shadow_expr.__rxor__(other.shadow_expr))
        else:
            ret_val = DifferenceExpression(self.origin_expr.__rxor__(other), self.shadow_expr.__rxor__(other))

        return ret_val

    def __ror__(self, other):
        if isinstance(other, DifferenceExpression):
            ret_val = DifferenceExpression(self.origin_expr.__ror__(other.origin_expr), self.shadow_expr.__ror__(other.shadow_expr))
        else:
            ret_val = DifferenceExpression(self.origin_expr.__ror__(other), self.shadow_expr.__ror__(other))

        return ret_val


# method to create a shadow expression for INT type symbolic and shadow Integer
def create_shadow(origin_expr, shadow_expr):
    if isinstance(origin_expr, DifferenceExpression):
        origin_expr = origin_expr.origin_expr

    if isinstance(shadow_expr, DifferenceExpression):
        shadow_expr = shadow_expr.shadow_expr

    return DifferenceExpression(origin_expr=origin_expr, shadow_expr=shadow_expr).check_to_merge()