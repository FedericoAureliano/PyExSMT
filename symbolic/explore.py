# Copyright: see copyright.txt

from collections import deque
import logging

from .path_to_constraint import PathToConstraint
from .invocation import FunctionInvocation
from .symbolic_types import symbolic_object, SymbolicObject

from pysmt.shortcuts import *


class ExplorationEngine:
    def __init__(self, funcinv, solver="z3"):
        self.invocation = funcinv
        # the input to the function
        self.symbolic_inputs = {}  # string -> SymbolicObject
        # initialize
        for n in funcinv.getNames():
            self.symbolic_inputs[n] = funcinv.createArgumentValue(n)

        self.constraints_to_solve = deque([])
        self.num_processed_constraints = 0

        self.path = PathToConstraint(lambda c : self.addConstraint(c))
        # link up SymbolicObject to PathToConstraint in order to intercept control-flow
        symbolic_object.SymbolicObject.SI = self.path

        self.solver = Solver(solver)
        self.solver.solve() # generate initial values
        # link up SymbolicObject to the Solver to get concrete values during execution
        symbolic_object.SymbolicObject.SOLVER = self.solver 

        # outputs
        self.generated_inputs = []
        self.execution_return_values = []

    def addConstraint(self, constraint):
        logging.debug("ADDING CONSTRAINT: %s" %(constraint.__repr__()))
        self.constraints_to_solve.append(constraint)

    def explore(self, max_iterations=0):
        self._oneExecution()
        
        iterations = 1
        if max_iterations != 0 and iterations >= max_iterations:
            logging.debug("Maximum number of iterations reached, terminating")
            return self.generated_inputs, self.execution_return_values, self.path

        while not self._isExplorationComplete():
            selected = self.constraints_to_solve.popleft()
            if selected.processed:
                continue		

            logging.debug("SELECTED CONSTRAINT: %s" % selected.__repr__())
            asserts, query = selected.getAssertsAndQuery()
            self._find_counterexample(asserts, query)

            if not self.solver.last_result:
                continue

            self._oneExecution(selected)

            iterations += 1			
            self.num_processed_constraints += 1

            if max_iterations != 0 and iterations >= max_iterations:
                logging.debug("Maximum number of iterations reached, terminating")
                break

        return self.generated_inputs, self.execution_return_values, self.path

    # private

    def _isExplorationComplete(self):
        num_constr = len(self.constraints_to_solve)
        if num_constr == 0:
            logging.info("EXPLORATION COMPLETE")
            return True
        else:
            logging.debug("%d constraints yet to solve (total: %d, already solved: %d)" % (num_constr, self.num_processed_constraints + num_constr, self.num_processed_constraints))
            return False

    def _get_concr_value(self,v):
        if isinstance(v,SymbolicObject):
            return v.get_concr_value()
        else:
            return v

    def _recordInputs(self):
        args = self.symbolic_inputs
        inputs = [(k, self._get_concr_value(args[k])) for k in args]
        self.generated_inputs.append(inputs)
        logging.debug("RECORDING INPUTS: %s" %(inputs))

    def _oneExecution(self,expected_path=None):
        logging.debug("EXPECTED PATH: %s" %(expected_path))
        self._recordInputs()
        logging.info("USING INPUTS: %s" %(self.generated_inputs[-1]))
        self.path.reset(expected_path)
        ret = self.invocation.callFunction(self.symbolic_inputs)
        logging.info("RETURN: %s" %(ret))
        self.execution_return_values.append(ret)

    def _find_counterexample(self, asserts, query):
        assumptions = [self._predToSMT(p) for p in asserts] + [Not(self._predToSMT(query))]
        logging.debug("SOLVING: %s" %(assumptions))
        self.solver.solve(assumptions)

    def _predToSMT(self, pred):
        if not pred.result:
            ret = Not(pred.symtype.expr)
        else:
            ret = pred.symtype.expr
        logging.debug("PREDICATE: %s" %(ret))
        return ret
        
