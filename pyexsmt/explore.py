# Copyright: see copyright.txt

from collections import deque
import logging

from pyexsmt.path_to_constraint import PathToConstraint
from pyexsmt import pred_to_smt
from pyexsmt.symbolic_types import symbolic_object
from pyexsmt.symbolic_types.symbolic_object import to_pysmt

from pysmt.shortcuts import *


class ExplorationEngine:
    def __init__(self, funcinv, solver, max_iterations=0, max_depth=0, mod=None):
        self.invocation      = funcinv
        self.max_iterations  = max_iterations
        self.symbolic_inputs = {}  # string -> SymbolicObject
        # initialize
        for n in funcinv.get_names():
            self.symbolic_inputs[n] = funcinv.create_arg_value(n)
        self.num_processed_constraints = 0
        self.path = PathToConstraint(solver, max_depth, mod)
        # link up SymbolicObject to PathToConstraint in order to intercept control-flow
        symbolic_object.SymbolicObject.SI = self.path
        # link up SymbolicObject to the Solver to get concrete values during execution
        symbolic_object.SymbolicObject.SOLVER = self.path.solver

    def explore(self, funcs=[]):
        self._one_execution(funcs)
        
        iterations = 1
        if self.max_iterations != 0 and iterations >= self.max_iterations:
            logging.debug("Maximum number of iterations reached, terminating")
            return self.path

        while not self.path.is_exploration_complete():
            selected = self.path.get_next_constraint()
            if selected.processed:
                continue		

            logging.debug("SELECTED CONSTRAINT: %s", selected)
            model = self.path.solve_constraint(selected)

            if not model:
                continue

            self._one_execution(funcs, selected)

            iterations += 1

            if self.max_iterations != 0 and iterations >= self.max_iterations:
                logging.debug("Maximum number of iterations reached, terminating")
                break

        return self.path

    def _one_execution(self, funcs=[], expected_path=None):
        self.path.shadowing = False
        symbolic_object.SymbolicObject.SI = self.path
        self.path.record_inputs(self.symbolic_inputs)
        logging.info("USING INPUTS: %s", self.path.generated_inputs[-1])
        logging.debug("EXPECTED PATH: %s", expected_path)

        self.path.reset(expected_path)

        try:
            ret = self.invocation.call_function(self.symbolic_inputs, funcs)
        except Exception:
            ret = None

        logging.debug("CURRENT CONSTARINT: %s", self.path.current_constraint)
        logging.info("RETURN: %s", ret)

        self.path.record_output(ret)
        return ret

    def _one_shadow_execution(self, funcs=[]):
        self.path.shadowing = True
        symbolic_object.SymbolicObject.SI = self.path
        try:
            ret = self.invocation.call_function(self.symbolic_inputs, funcs)
        except Exception:
            ret = None
        return ret

class ShadowExplorationEngine:
    def __init__(self, funcinv, shadowinv, solver, max_iterations=0, max_depth=0, mod=None):
        self.solver = solver
        self.engines = []
        self.engines.append(ExplorationEngine(funcinv, solver, max_iterations, max_depth, mod))
        self.engines.append(ExplorationEngine(shadowinv, solver, max_iterations, max_depth, mod))
        self.lead = 0
        self.max_iterations = max_iterations

    def explore(self, funcs=[], lazy=True):
        original = self.engines[0]
        shadow = self.engines[1]
        r1, r2 = self._one_execution(funcs)
        if lazy:
            if not self.solver.get_py_value(Equals(to_pysmt(r1), to_pysmt(r2))):
                logging.info("COUNTER! %s != %s", repr(r1), repr(r2))
                print("ORIG #Paths: %d" % len(original.path.generated_inputs))
                print("UPGR #Paths: %d" % len(shadow.path.generated_inputs))
                return self.engines[self.lead-1].path.generated_inputs[-1]

        iterations = 1
        if self.max_iterations != 0 and iterations >= self.max_iterations:
            logging.debug("Maximum number of iterations reached, terminating")
            return (original.path, shadow.path)

        while not self.is_exploration_complete():
            selected = self.get_next_constraints()

            logging.debug("SELECTED CONSTRAINT: %s", selected)
            model = self.engines[self.lead].path.solve_constraint(selected)

            if not model:
                continue

            #TODO avoid executing things unnecesarily? 
            r1, r2 = self._one_execution(funcs, selected)

            if lazy:
                if not self.solver.get_py_value(Equals(to_pysmt(r1), to_pysmt(r2))):
                    logging.info("COUNTER! %s != %s", repr(r1), repr(r2))
                    print("ORIG #Paths: %d" % len(original.path.generated_inputs))
                    print("UPGR #Paths: %d" % len(shadow.path.generated_inputs))
                    return self.engines[self.lead-1].path.generated_inputs[-1]

            iterations += 1

            if self.max_iterations != 0 and iterations >= self.max_iterations:
                logging.debug("Maximum number of iterations reached, terminating")
                break

        return (original.path, shadow.path)

    def get_next_constraints(self):
        lead = self.engines[self.lead]
        follow = self.engines[self.lead-1]
        if not lead.path.is_exploration_complete():
            return lead.path.get_next_constraint()
        elif not follow.path.is_exploration_complete():
            self.lead = (self.lead + 1) % 2
            return follow.path.get_next_constraint()
        else:
            raise ValueError("No Constraints left!")

    def is_exploration_complete(self):
        return all([x.path.is_exploration_complete() for x in self.engines])

    def _one_execution(self, funcs, selected=None):
        if selected is None:
            r1 = self.engines[self.lead]._one_execution(funcs)
            r2 = self.engines[self.lead-1]._one_execution(funcs)
        else:
            r1 = self.engines[self.lead]._one_execution(funcs, selected)
            r2 = self.engines[self.lead-1]._one_shadow_execution(funcs)
        self.lead = (self.lead + 1) % 2
        return r1, r2
