# Copyright: see copyright.txt

import logging

from pyexsmt.predicate import Predicate
from pyexsmt.constraint import Constraint

from pyexsmt import pred_to_smt
from pysmt.shortcuts import *

class PathToConstraint:
    def __init__(self, add):
        self.constraints = {}
        self.add = add
        self.root_constraint = Constraint(None, None)
        self.current_constraint = self.root_constraint
        #constraint of the old program
        self.current_shadow_constraint = self.root_constraint
        #constraint of the new program
        self.current_mirror_constraint = self.root_constraint
        self.expected_path = None
        self.max_depth = 0
        self.mod = None
        self.diverge = False

    def reset(self,expected):
        self.diverge = False
        self.current_constraint = self.root_constraint
        self.current_shadow_constraint = self.root_constraint
        self.current_mirror_constraint=self.root_constraint
        if expected is None:
            self.expected_path = None
        else:
            self.expected_path = []
            tmp = expected
            while tmp.predicate is not None:
                self.expected_path.append(tmp.predicate)
                tmp = tmp.parent

    def which_branch(self, branch, symbolic_type, shadow_branch, shadow_type, shadowLeadding = False):
        """ This function acts as instrumentation.
        Branch can be either True or False."""

        if self.max_depth > 0 and self.current_constraint.get_length() >= self.max_depth:
            logging.debug("Max Depth (%d) Reached", self.max_depth)
            return

        # add both possible predicate outcomes to constraint (tree)
        p = Predicate(symbolic_type, branch)
        p.negate()
        cneg = self.current_constraint.find_child(p, shadowLeadding)
        p.negate()
        cpos = self.current_constraint.find_child(p, shadowLeadding)
        c = cpos
        c_mirror = cpos

        p_shadow = Predicate(shadow_type, shadow_branch)
        p_shadow.negate()
        cneg_shadow = self.current_constraint.find_child(p_shadow, shadowLeadding)
        p_shadow.negate()
        c_shadow = self.current_constraint.find_child(p_shadow, shadowLeadding)
        #c_shadow_mirror = c_shadow

        #two bool to record the current state of p and p_shadow
        p_bool = branch;
        p_shadow_bool = shadow_branch;

        constraint_find = False;

        #continue exploration if path does not diverage
        diverage = p_bool != p_shadow_bool



        #if program has no diverging paths, perform 4-way forking
        #if program was executed on the shadow version, do not perform 4 way forking
        if (not self.diverge and not shadowLeadding):
            #perform 4 way forking
            #follow the concrete input and create path constraint
            if not constraint_find:
                asserts = [pred_to_smt(p) for p in self.current_constraint.get_asserts()]
                if (self.mod is not None and not is_sat(
                        And(self.mod, pred_to_smt(p), pred_to_smt(p_shadow), *asserts))):
                    logging.debug("Path pruned by mod (%s): %s %s", self.mod, c, p)
                else:
                    pMerged = p.AND(p_shadow)
                    c = self.current_constraint.find_child(pMerged)
                    if (c is None):
                        c = self.current_constraint.add_child(pMerged, four_way =True)
                        logging.debug("New constraint: %s", c)
                        self.add(c)
                    self.diverge = diverage or self.diverge
                    constraint_find = True
                    # TODO also add the shadow constraint to shadow child list since both version follow the sme path
                    p_shadow_copy = Predicate(p_shadow.symtype, p_shadow.result)
                    c_shadow_mirror = self.current_shadow_constraint.find_child(p_shadow_copy, shadow=True)
                    if c_shadow_mirror is None:
                        c_shadow_mirror=self.current_shadow_constraint.add_child(p_shadow_copy, shadow=True)

                    p_copy = Predicate(p.symtype, p.result)
                    c_mirror = self.current_mirror_constraint.find_mirror_child(p_copy)
                    if c_mirror is None:
                        c_mirror = self.current_mirror_constraint.add_mirror_child(p_copy)

            #Then we try to find all feasible diverging path from the 4-way forking
            #case 2, filp symbolic predicate but keep shadow the same
            if cneg is None and c_shadow is None and constraint_find:
                if (p_bool == branch):
                    p.negate()
                    p_bool = not branch
                if (p_shadow_bool != shadow_branch):
                    p_shadow.negate()
                    p_shadow_bool = shadow_branch
                asserts = [pred_to_smt(p) for p in self.current_constraint.get_asserts()]
                if (self.mod is not None and not is_sat(
                        And(self.mod, pred_to_smt(p), pred_to_smt(p_shadow), *asserts))) or (
                        not is_sat(And(pred_to_smt(p), pred_to_smt(p_shadow), *asserts))):
                    logging.debug("Path is not feasible: %s %s", c.parent, p.AND(p_shadow))
                else:
                    priority = not diverage
                    c_possible_divergence = c.add_siblings(p.AND(p_shadow), priority)
                    logging.debug("New possible divergence constraint: %s", c_possible_divergence)

            # case 3, flip  shadow predicate but keep symbolic the same
            if cpos is None and cneg_shadow is None and constraint_find:
                if (p_bool != branch):
                    p.negate()
                    p_bool =  branch
                if (p_shadow_bool == shadow_branch):
                    p_shadow.negate()
                    p_shadow_bool = not shadow_branch
                asserts = [pred_to_smt(p) for p in self.current_constraint.get_asserts()]
                if (self.mod is not None and not is_sat(
                        And(self.mod, pred_to_smt(p), pred_to_smt(p_shadow), *asserts))) or (
                        not is_sat(And(pred_to_smt(p), pred_to_smt(p_shadow), *asserts))):
                    logging.debug("Path is not feasible: %s %s", c.parent, p.AND(p_shadow))
                else:
                    priority = not diverage
                    c_possible_divergence = c.add_siblings(p.AND(p_shadow), priority)
                    logging.debug("New possible divergence constraint: %s", c_possible_divergence)

            # case 4, flip both shadow and symbolic predicate
            if cneg is None and cneg_shadow is None and constraint_find:
                if (p_bool == branch):
                    p.negate()
                    p_bool =  not branch
                if (p_shadow_bool == shadow_branch):
                    p_shadow.negate()
                    p_shadow_bool = not shadow_branch
                asserts = [pred_to_smt(p) for p in self.current_constraint.get_asserts()]
                if (self.mod is not None and not is_sat(
                        And(self.mod, pred_to_smt(p), pred_to_smt(p_shadow), *asserts))) or (
                        not is_sat(And(pred_to_smt(p), pred_to_smt(p_shadow), *asserts))):
                    logging.debug("Path is not feasible: %s %s", c.parent, p.AND(p_shadow))
                else:
                    priority = diverage
                    c_possible_divergence = c.add_siblings(p.AND(p_shadow), priority)
                    logging.debug("New possible divergence constraint: %s", c_possible_divergence)


        #if program has aleady diverged, then only perform 2 way forking as normal symbolic execution
        if cpos is None and not constraint_find and (shadowLeadding or self.diverge):
            asserts = [pred_to_smt(p) for p in self.current_constraint.get_asserts()]
            if self.mod is not None and not is_sat(And(self.mod, pred_to_smt(p), *asserts)):
                logging.debug("Path pruned by mod (%s): %s %s", self.mod, c, p)
                return
            c = self.current_constraint.find_child(p, shadowLeadding)
            if ( c is None):
                c = self.current_constraint.add_child(p, shadowLeadding)
                # we add the new constraint to the queue of the engine for later processing
                logging.debug("New constraint: %s", c)
                self.add(c)
                constraint_find = True

            if (not shadowLeadding):
                p_copy = Predicate(p.symtype, p.result)
                c_mirror = self.current_mirror_constraint.find_mirror_child(p_copy)
                if c_mirror is None:
                    c_mirror = self.current_mirror_constraint.add_mirror_child(p_copy)

            
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
                print("Replay mismatch (done=",done,")")
                print(expected)
                print(c.predicate)

        if cneg is not None:
            # We've already processed both
            cneg.processed = True
            c.processed = True
            logging.debug("Processed constraint: %s", c)

        self.current_constraint = c
        if not shadowLeadding:
            self.current_mirror_constraint = c_mirror
            if not self.diverge:
                self.current_shadow_constraint = c_shadow_mirror
