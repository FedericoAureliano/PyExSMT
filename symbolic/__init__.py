import logging

from symbolic.symbolic_types import SymbolicObject

from pysmt.shortcuts import *

def pred_to_SMT(pred):
    if pred is None:
        return TRUE()

    if not pred.result:
        ret = Not(pred.symtype.expr)
    else:
        ret = pred.symtype.expr

    logging.debug("PREDICATE: %s" %(ret))
    return ret

def get_concr_value(v):
    if isinstance(v,SymbolicObject):
        return v.get_concr_value()
    else:
        return v