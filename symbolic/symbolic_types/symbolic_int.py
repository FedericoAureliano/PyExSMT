# Copyright: copyright.txt

from . symbolic_object import SymbolicObject

from pysmt.shortcuts import INT

class SymbolicInteger(SymbolicObject):
    def __init__(self, expr, name = "se"):
        SymbolicObject.__init__(self, expr, name, INT)