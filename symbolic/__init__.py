import logging
import re

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

types ={"INT": INT,\
        "int": INT,\
        "Int": INT}

def parse_types(type_list):
    '''
    take a list of two strings, type_list.
    type_list[0] is the return type.
    type_list[1] is the argument types.
    something like ["INT", "[INT,INT]"].
    Return the correct type list.
    E.g. [INT, [INT, INT]]
    '''
    return_type = types[type_list[0]]
    arg_types = re.findall('\w+', type_list[1])
    arg_types = [types[a] for a in arg_types]
    return [return_type, arg_types]