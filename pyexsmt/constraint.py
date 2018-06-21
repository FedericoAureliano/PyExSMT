# Copyright: see copyright.txt

import logging
from pysmt.shortcuts import *
from pyexsmt import pred_to_smt
from threading import Thread, Lock



class Constraint:
    cnt = 0
    # To ensure one solver is being ran at one time
    Constraint_Solving_lock = Lock()
    """A constraint is a list of predicates leading to some specific
       position in the code."""
    def __init__(self, parent, last_predicate):
        self.inputs = None
        self.predicate = last_predicate
        self.effect = None
        self.processed = False
        self.parent = parent
        self.children = []
        self.id = self.__class__.cnt
        self.__class__.cnt += 1
        self.solver = None
        self.solving_thread = None

    def __eq__(self, other):
        """Two Constraints are equal iff they have the same chain of predicates"""
        if isinstance(other, Constraint):
            if not self.predicate == other.predicate:
                return False
            return self.parent is other.parent
        else:
            return False

    def get_asserts_and_query(self):
        asserts = self.get_asserts()
        return asserts, self.predicate	       

    def get_asserts(self):
        # collect the assertions
        if self.parent is None:
            return []
        asserts = []
        tmp = self.parent
        while tmp.predicate is not None:
            asserts.append(tmp.predicate)
            tmp = tmp.parent

        return asserts

    def get_length(self):
        if self.parent == None:
            return 0
        return 1 + self.parent.get_length()

    def __str__(self):
        return str(self.predicate) + "  (processed: %s, path_len: %d)" % (self.processed,self.get_length())

    def __repr__(self):
        s = repr(self.predicate) + " (processed: %s)" % (self.processed)
        if self.parent is not None:
            s += "\n  path: %s" % repr(self.parent)
        return s

    def find_child(self, predicate):
        for c in self.children:
            if predicate == c.predicate:
                return c
        return None

    def add_child(self, predicate):
        assert(self.find_child(predicate) is None)
        c = Constraint(self, predicate)
        self.children.append(c)
        return c

    def solveConstraint(self):
        asserts, query =  self.get_asserts_and_query()
        self._find_counterexample(asserts, query)

    def _find_counterexample(self, asserts, query):
        assumptions = [pred_to_smt(p) for p in asserts] + [Not(pred_to_smt(query))]
        logging.debug("SOLVING: %s", assumptions)
        Constraint.Constraint_Solving_lock.acquire()
        try:
            self.solver.solve(assumptions)
        except:
            raise
        finally:
            Constraint.Constraint_Solving_lock.release()



    def __hash__(self):
        return hash(id(self))

def solve_constraint_function(constraint):
    # only allow 1 constraint to be solved at 1 time
    constraint.solveConstraint()


def submit_constraint_sovling(constraint, slover="z3"):
    # create the solver and assign constraint solving to a different thread
    if constraint.solving_thread is None:
        constraint.solver= Solver(slover)
        constraint.solving_thread = Thread(target=solve_constraint_function, args={constraint})
        constraint.solving_thread.start()


