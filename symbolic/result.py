import logging
from graphviz import Source
from collections import deque

from symbolic import pred_to_SMT, get_concr_value, match_SMT_type
from symbolic.symbolic_types import SymbolicObject
from symbolic.symbolic_types.symbolic_object import wrap

from pysmt.shortcuts import *

class Result(object):
    def __init__(self, path):
        self.path = path
        self.generated_inputs = []
        self.execution_return_values = []
        self.list_rep = None

    def record_inputs(self, inputs):
        inputs = [(k, get_concr_value(inputs[k])) for k in inputs]
        self.generated_inputs.append(inputs)
        logging.debug("RECORDING INPUTS: %s" %(inputs))

    def record_output(self, ret):
        self.path.current_constraint.effect = wrap(ret)
        if isinstance(ret, SymbolicObject):
            ret = ret.get_concr_value()
        self.execution_return_values.append(ret)

    def to_dot(self, filename):
        header = "digraph {\n"
        footer = "}\n"
        if self.list_rep is None:
            self.list_rep = self._to_list_rep(self.path.root_constraint)
        dot = self._to_dot(self.list_rep)
        dot = header + dot + footer
        s = Source(dot, filename=filename+".dot", format="png")
        s.view()

    def _to_dot(self, list_rep, level = 0):
        if isinstance(list_rep, list) and len(list_rep) == 3:
            rep = list_rep[0]
            dot = "\"%s%d\" [ label=\"%s\" ];\n" % (rep, level, rep)

            for slot in range(1,3):
                child = list_rep[slot]
                if child is None:
                    continue
                crep = child[0] if isinstance(child, list) else child
                crep = str(crep).replace('"', '\\\"')
                dot += "\"%s%d\" -> \"%s%d\" [ label=\"%d\" ];\n" %(rep, level, crep, level+1, slot % 2)
                dot += self._to_dot(child, level+1)
            return dot
        elif list_rep is not None:
            list_rep = str(list_rep).replace('"', '\\\"')
            return "\"%s%d\" [ label=\"%s\" ];\n" % (list_rep, level, list_rep)
        else:
            return ""

    def to_summary(self, unknown = Symbol('Unknown', INT)):
        if self.list_rep is None:
            self.list_rep = self._to_list_rep(self.path.root_constraint)
        summary = self._to_summary(self.list_rep, unknown)
        return summary

    def _to_summary(self, list_rep, unknown):
        if isinstance(list_rep, list) and len(list_rep) == 3:
            return Ite(list_rep[0], self._to_summary(list_rep[1], unknown), self._to_summary(list_rep[2], unknown))
        elif list_rep is not None:
            return match_SMT_type(list_rep, unknown.get_type())
        else:
            return unknown

    def _to_list_rep(self, node):
        if node is None:
            return None
        elif len(node.children) == 2:
            if node.children[0].predicate.symtype.symbolicEq(node.children[1].predicate.symtype):
                left = node.children[0] if node.children[0].predicate.result else node.children[1]
                right = node.children[1] if not node.children[1].predicate.result else node.children[0]
                return [pred_to_SMT(left.predicate), self._to_list_rep(left), self._to_list_rep(right)]
            else:
                print(node.children)
                raise ValueError("Should not be possible! Two children of a constraint should have the same predicate.")
        elif len(node.children) == 1:
            left = node.children[0] if node.children[0].predicate.result else None
            right = node.children[0] if not node.children[0].predicate.result else None
            return [pred_to_SMT(left.predicate if left else right.predicate), self._to_list_rep(left), self._to_list_rep(right)]
        elif len(node.children) == 0:
            return node.effect

        raise ValueError("Should not be possible! Can't have more than two children.")
