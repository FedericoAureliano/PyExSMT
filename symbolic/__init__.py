import logging

from .symbolic_types import SymbolicObject

from pysmt.shortcuts import *

def pred_to_SMT(pred):
    t = pred.symtype.expr.get_type()
    if t == BOOL:
        if not pred.result:
            ret = Not(pred.symtype.expr)
        else:
            ret = pred.symtype.expr
    elif t == INT:
        if not pred.result:
            ret = Equals(pred.symtype.expr, Int(0))
        else:
            ret = NotEquals(pred.symtype.expr, Int(0))
    else:
        raise NotImplementedError("%s predicate processing not implemented yet" % t)

    logging.debug("PREDICATE: %s" %(ret))
    return ret

def get_concr_value(v):
    if isinstance(v,SymbolicObject):
        return v.get_concr_value()
    else:
        return v