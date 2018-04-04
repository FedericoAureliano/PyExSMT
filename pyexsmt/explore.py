# Copyright: see copyright.txt

from collections import deque
import logging

from pyexsmt.path_to_constraint import PathToConstraint
from pyexsmt import pred_to_smt
from pyexsmt.symbolic_types import symbolic_object
from pyexsmt.result import Result
from pyexsmt.symbolic_types.symbolic_object import compare_symbolic_and_concrete_value

from pysmt.shortcuts import *


class ExplorationEngine:

    def __init__(self, funcinv, solver="z3"):
        self.invocation = funcinv
        # the input to the function
        self.symbolic_inputs = {}  # string -> SymbolicObject
        # initialize
        for n in funcinv.get_names():
            self.symbolic_inputs[n] = funcinv.create_arg_value(n)

        #create a SHADOW_HANDLER to control shadow annotation injection


        self.constraints_to_solve = deque([])
        self.num_processed_constraints = 0

        self.path = PathToConstraint(lambda c : self.add_constraint(c))
        # link up SymbolicObject to PathToConstraint in order to intercept control-flow
        symbolic_object.SymbolicObject.SI = self.path

        self.solver = Solver(solver)
        self.solver.solve() # generate initial values
        # link up SymbolicObject to the Solver to get concrete values during execution
        symbolic_object.SymbolicObject.SOLVER = self.solver 

        # outputs
        self.result = Result(self.path)

        self.diverge = False;

    def add_constraint(self, constraint):
        logging.debug("ADDING CONSTRAINT: %s", repr(constraint))
        if constraint not in self.constraints_to_solve:
            self.constraints_to_solve.append(constraint)

    def explore(self, max_iterations=0, max_depth=0, funcs=[], mod=None):
        self.path.max_depth = max_depth
        self.path.mod = mod

        symbolic_ret = self._one_execution(funcs)
        # if we found a value mismatch across 2 versions, we will get a list of 2 rets, print out the values as counter example
        if (isinstance(symbolic_ret, list) and len(symbolic_ret) > 1):
            if (not self.result.mismatch_constraints is None):
                self.solver.solve(self.result.mismatch_constraints)
            self.print_counter_example(self.symbolic_inputs, symbolic_ret[0], symbolic_ret[1])
            return None


        #if execution path diverged, execute on the old version to validate program's return value
        if (self.diverge):
            shadow_ret = self._one_execution(funcs, shadowLeading=True)
            mirror_asserts, mirror_query = self.path.current_constraint.get_asserts_and_query()
            shadow_ret = self._one_execution(funcs, shadowLeading=True)
            shadow_assert, shadow_query = self.path.current_constraint.get_asserts_and_query()
            asserts = [pred_to_smt(p) for p in  mirror_asserts + shadow_assert]
            query = [ pred_to_smt(mirror_query), pred_to_smt(shadow_query)]
            collection = asserts + query
            result, diff_constraint = compare_symbolic_and_concrete_value(symbolic_ret, shadow_ret, collection)
            if (result > 0):
                self.print_counter_example(self.symbolic_inputs, symbolic_ret, shadow_ret)
                return None

        
        iterations = 1
        if max_iterations != 0 and iterations >= max_iterations:
            logging.debug("Maximum number of iterations reached, terminating")
            return self.result

        while not self._is_exploration_complete():
            selected = self.constraints_to_solve.popleft()
            if selected.processed:
                continue		

            logging.debug("SELECTED CONSTRAINT: %s", repr(selected))
            asserts, query = selected.get_asserts_and_query()
            if (selected.siblings is None):
                query = self._find_counterexample(asserts, query)
            else:
                #if 4 way forking is used, then we will explore the siblings
                query= self._find_conterexample_shadow(asserts, selected)


            if not self.solver.last_result:
                continue

            #if the selected input has already been attempted, skip to the next constraint
            symbolic_ret = self._one_execution(funcs)
            if (symbolic_ret is None):
                self.num_processed_constraints += 1
                continue

            #if we found a value mismatch across 2 versions, we will get a list of 2 rets, print out the values as counter example
            if (isinstance(symbolic_ret, list) and len(symbolic_ret) > 1):
                #check if we need to re-computer the input set in order to cause the difference
                if (not self.result.mismatch_constraints is None):
                    self.solver.solve(self.result.mismatch_constraints)
                self.print_counter_example(self.symbolic_inputs, symbolic_ret[0], symbolic_ret[1])
                return None

            if self.diverge:
                mirror_asserts, mirror_query= self.path.current_constraint.get_asserts_and_query()
                shadow_ret = self._one_execution(funcs, shadowLeading=True)
                shadow_assert, shadow_query = self.path.current_constraint.get_asserts_and_query()
                asserts = [pred_to_smt(p) for p in asserts + mirror_asserts + shadow_assert]
                query = [query, pred_to_smt(mirror_query), pred_to_smt(shadow_query)]
                collection = asserts + query
                result, diff_constraint = compare_symbolic_and_concrete_value(symbolic_ret, shadow_ret, collection)
                if (result > 0):
                    # return 1 means there could a input value set that cause the return being different, solve for the input set
                    if (result == 1):
                        self.solver.solve(collection + [diff_constraint])
                    self.print_counter_example(self.symbolic_inputs, symbolic_ret, shadow_ret)
                    return None

            iterations += 1			
            self.num_processed_constraints += 1

            if max_iterations != 0 and iterations >= max_iterations:
                logging.debug("Maximum number of iterations reached, terminating")
                break

        return self.result

    def print_counter_example (self, symbolic_inputs, return_new, return_shadow, proven_inequaility=False):
        input_string = ""
        sep = ""
        for key,value in symbolic_inputs.items():
            input_string+=sep
            sep = " , "
            input_string+=str(key)
            input_string+=("=")
            input_string+=str(value)
        print("Find a counter example with input: %s" % input_string)
        if (isinstance(return_new, symbolic_object.SymbolicObject)):
            return_new = str(return_new.expr) + " with concrete value: " + str(return_new.get_concr_value())

        if (isinstance(return_shadow, symbolic_object.SymbolicObject)):
            return_shadow = str(return_shadow.expr) + " with value: " + str(return_shadow.get_concr_value())

        print("New Version returns %s, Old Version returns %s" % (return_new, return_shadow))

    def _is_exploration_complete(self):
        num_constr = len(self.constraints_to_solve)
        if num_constr == 0:
            logging.info("EXPLORATION COMPLETE")
            return True
        else:
            logging.debug("%d constraints yet to solve (total: %d, already solved: %d)", \
            num_constr, self.num_processed_constraints + num_constr, self.num_processed_constraints)
            return False

    def _reset_shadow(self, sInput):
        for _, value in sInput.items():
            if isinstance(value, symbolic_object.SymbolicObject):
                value.reset_shadow()

    def _one_execution(self, funcs=[], expected_path=None, shadowLeading = False):

        if (shadowLeading):
            logging.debug("PATH has diverged, execute program on shadow version")
            symbolic_object.SymbolicObject.SHADOW_LEADING = True
        logging.debug("EXPECTED PATH: %s", expected_path)


        #if input has already been attempted, skip execution
        if (not self.result.record_inputs(self.symbolic_inputs) and not shadowLeading):
            logging.debug("Duplicated INPUTS: %s", self.symbolic_inputs)
            return None


        #reset shadow value for symbolic input
        self._reset_shadow(self.symbolic_inputs)
        logging.info("USING INPUTS: %s", self.result.generated_inputs[-1])

        self.path.reset(expected_path)
        ret = self.invocation.call_function(self.symbolic_inputs, funcs)
        symbolic_object.SymbolicObject.SHADOW_LEADING = False

        logging.debug("CURRENT CONSTARINT: %s", repr(self.path.current_constraint))
        logging.info("RETURN: %s", ret)

        self.diverge = self.path.diverge
        return self.result.record_output(ret, shadowLeading, compare_symbolic_shadow_result= (not self.diverge))



    def _find_counterexample(self, asserts, query):
        assumptions = [pred_to_smt(p) for p in asserts] + [Not(pred_to_smt(query))]
        logging.debug("SOLVING: %s", assumptions)
        self.solver.solve(assumptions)
        return Not(pred_to_smt(query))

    def _find_conterexample_shadow(self, asserts, constraint):
        query = constraint.siblings.pop(0)
        assumptions = [pred_to_smt(p) for p in asserts] + [(pred_to_smt(query))]
        logging.debug("SOLVING: %s", assumptions)
        self.solver.solve(assumptions)
        if (len(constraint.siblings) > 0):
            self.constraints_to_solve.appendleft(constraint)
            constraint.processed = False;
        else:
            constraint.processed = True;

        return pred_to_smt(query)


