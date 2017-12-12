import logging
from graphviz import Source

from symbolic import pred_to_SMT, get_concr_value
from .symbolic_types import SymbolicObject

from pysmt.shortcuts import *

class Result(object):
    def __init__(self, path, summary=False):
        self.path = path
        self.summary = [] if summary else None
        self.generated_inputs = []
        self.execution_return_values = []

    def record_inputs(self, inputs):
        inputs = [(k, get_concr_value(inputs[k])) for k in inputs]
        self.generated_inputs.append(inputs)
        logging.debug("RECORDING INPUTS: %s" %(inputs))

    def record_output(self, ret):
        if not self.summary is None:
            asserts = self.path.current_constraint.get_asserts() + [self.path.current_constraint.predicate]
            asserts = [pred_to_SMT(p) for p in asserts]
            logging.debug("PATH: %s" % (asserts))
            self.summary.append((And(asserts), ret))
        
        if isinstance(ret, SymbolicObject):
            ret = ret.get_concr_value()
        self.execution_return_values.append(ret)

    def to_dot(self, filename):
        temp = self.path.toDot()
        s = Source(temp, filename=filename+".dot", format="png")
        s.view()
    
    def to_summary(self):
        print("\nSUMMARY:")
        for p,e in self.summary:
            print("PATH: %s" % p)
            print("EFFECT: %s\n" % e.__repr__())