# Copyright: see copyright.txt

from symbolic.symbolic_types.symbolic_int import SymbolicInteger
from symbolic.symbolic_types.symbolic_int import SymbolicObject

def getSymbolic(v):
    exported = [(int, SymbolicInteger), (bool, SymbolicObject)]
    for (t, s) in exported:
        if isinstance(v, t):
            return s
    return None
