# Copyright: see copyright.txt

import logging
from graphviz import Source

from collections import deque

from pyexsmt.symbolic_types.symbolic_object import to_pysmt, is_instance_userdefined_and_newclass
from pyexsmt import pred_to_smt, get_concr_value, match_smt_type
from pyexsmt.symbolic_types import SymbolicObject
from pyexsmt.constraint import Constraint
from pyexsmt.predicate import Predicate

from pysmt.shortcuts import *

class PathToConstraint:
    def __init__(self, solver, max_depth, mod):
        self.solver = solver
        self.max_depth = max_depth
        if mod is not None:
            self.mod = mod
        else:
            self.mod = TRUE()
        # generate initial values
        self.solver.solve([self.mod])  

        self.root_constraint = Constraint(None, None)
        self.current_constraint = self.root_constraint
        self.expected_path = None
        self.constraints_to_solve = deque([])

        self.generated_inputs = []
        self.execution_return_values = []
        self.list_rep = None
        self.curr_id = 0

        self.shadowing = False

    def reset(self,expected):
        self.current_constraint = self.root_constraint
        if expected is None:
            self.expected_path = None
        else:
            self.expected_path = []
            tmp = expected
            while tmp.predicate is not None:
                self.expected_path.append(tmp.predicate)
                tmp = tmp.parent

    def which_branch(self, branch, symbolic_type):
        """ This function acts as instrumentation.
        Branch can be either True or False."""

        if self.max_depth > 0 and self.current_constraint.get_length() >= self.max_depth:
            logging.debug("Max Depth (%d) Reached", self.max_depth)
            return

        if self.shadowing:
            return

        # add both possible predicate outcomes to constraint (tree)
        p = Predicate(symbolic_type, branch)
        p.negate()
        cneg = self.current_constraint.find_child(p)
        p.negate()
        c = self.current_constraint.find_child(p)

        if c is None:
            asserts = [pred_to_smt(p) for p in self.current_constraint.get_asserts()]
            if self.mod is not None and not is_sat(And(self.mod, pred_to_smt(p), *asserts)):
                logging.debug("Path pruned by mod (%s): %s %s", self.mod, c, p)
                return

            c = self.current_constraint.add_child(p)

            # we add the new constraint to the queue of the engine for later processing
            logging.debug("New constraint: %s", c)
            self.add_constraint(c)
            
        # check for path mismatch
        # IMPORTANT: note that we don't actually check the predicate is the
        # same one, just that the direction taken is the same
        if self.expected_path != None and self.expected_path != []:
            expected = self.expected_path.pop()
            # while not at the end of the path, we expect the same predicate result.
            # At the end of the path, we expect a different predicate result
            done = self.expected_path == []
            logging.debug("DONE: %s; EXP: %s; C: %s", done, expected, c)
            if ( not done and expected.result != c.predicate.result or \
                done and expected.result == c.predicate.result ):
                logging.info("Replay mismatch (done=%s)",done)
                logging.info(expected)
                logging.info(c.predicate)

        if cneg is not None:
            # We've already processed both
            cneg.processed = True
            c.processed = True
            logging.info("Processed constraint: %s", c)

        self.current_constraint = c

    def add_constraint(self, c):
        self.constraints_to_solve.append(c)

    def get_next_constraint(self):
        return self.constraints_to_solve.popleft()

    def is_exploration_complete(self):
        return len(self.constraints_to_solve) == 0

    def solve_constraint(self, selected):
        #TODO Check if we already have a solution to it first
        #TODO Do local search if we have an almost solution?
        asserts, query = selected.get_asserts_and_query()
        assumptions = [self.mod] + [pred_to_smt(p) for p in asserts] + [Not(pred_to_smt(query))]
        self.solver.solve(assumptions)
        logging.debug("SOLVING: %s", assumptions)
        return self.solver.last_result

    def record_inputs(self, inputs):
        inputs = [(k, get_concr_value(inputs[k])) for k in inputs]
        self.generated_inputs.append(inputs)
        logging.debug("RECORDING INPUTS: %s", inputs)

    def record_output(self, ret):
        logging.info("RECORDING EFFECT: %s -> %s", self.current_constraint, repr(ret))

        self.current_constraint.effect = ret

        if isinstance(ret, SymbolicObject):
            ret = ret.get_concr_value()
        self.execution_return_values.append(ret)

    def to_dot(self, filename):
        header = "digraph {\n"
        footer = "}\n"
        if self.list_rep is None:
            self.list_rep = self._to_list_rep(self.root_constraint)
        dot = self._to_dot(self.list_rep)
        dot = header + dot + footer
        s = Source(dot, filename=filename+".dot", format="png")
        s.view()

    def _to_dot(self, list_rep):
        curr = self.curr_id
        if isinstance(list_rep, list) and len(list_rep) == 3:
            rep = list_rep[0]
            dot = "\"%s%d\" [ label=\"%s\" ];\n" % (rep, curr, rep)
            self.curr_id += 1

            for slot in range(1, 3):
                child = list_rep[slot]
                if child is None:
                    continue
                crep = child[0] if isinstance(child, list) else to_pysmt(child)
                crep = str(crep).replace('"', '\\\"')
                dot += "\"%s%d\" -> \"%s%d\" [ label=\"%d\" ];\n" \
                        %(rep, curr, crep, self.curr_id, slot%2)
                dot += self._to_dot(child)
            return dot
        elif list_rep is not None:
            list_rep = to_pysmt(list_rep)
            list_rep = str(list_rep).replace('"', '\\\"')
            temp = "\"%s%d\" [ label=\"%s\" ];\n" % (list_rep, curr, list_rep)
            self.curr_id += 1
            return temp
        else:
            return ""

    def to_summary(self, unknown=Symbol('Unknown', INT)):
        if self.list_rep is None:
            self.list_rep = self._to_list_rep(self.root_constraint)
        summary = self._to_summary(self.list_rep, unknown)
        return summary

    def _to_summary(self, list_rep, unknown):
        if isinstance(list_rep, list) and len(list_rep) == 3:
            return Ite(list_rep[0], self._to_summary(list_rep[1], unknown),\
                        self._to_summary(list_rep[2], unknown))
        elif list_rep is not None:
            if isinstance(list_rep, SymbolicObject) or not is_instance_userdefined_and_newclass(list_rep):
                return match_smt_type(to_pysmt(list_rep), unknown.get_type())
            else:
                print(list_rep, type(list_rep))
                raise TypeError("Summaries don't support object returns")
        else:
            return unknown

    def _to_list_rep(self, node):
        if node is None:
            return None
        children = node.children
        if len(children) == 2:
            if node.children[0].predicate.symtype.symbolic_eq(node.children[1].predicate.symtype):
                left = node.children[0] if node.children[0].predicate.result else node.children[1]
                right = node.children[1] if not node.children[1].predicate.result else node.children[0]
                return [pred_to_smt(left.predicate), self._to_list_rep(left), self._to_list_rep(right)]
            else:
                raise ValueError("Two children of a constraint should have the same predicate!")
        elif len(node.children) == 1:
            return [pred_to_smt(node.children[0].predicate), self._to_list_rep(node.children[0]), None]
        elif len(children) == 0:
            return node.effect

        raise ValueError("Should not be possible! Can't have more than two children.")
