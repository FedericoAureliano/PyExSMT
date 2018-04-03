import logging
from graphviz import Source

from pyexsmt import pred_to_smt, get_concr_value, match_smt_type
from pyexsmt.symbolic_types import SymbolicObject
from pyexsmt.symbolic_types.symbolic_object import to_pysmt, is_instance_userdefined_and_newclass

from pysmt.shortcuts import *

class Result(object):
    def __init__(self, path):
        self.path = path
        self.generated_inputs = []
        self.execution_return_values = []
        self.list_rep = None
        self.curr_id = 0

    def record_inputs(self, inputs):
        inputs = [(k, get_concr_value(inputs[k])) for k in inputs]
        if inputs in self.generated_inputs:
            return False
        self.generated_inputs.append(inputs)
        logging.debug("RECORDING INPUTS: %s", inputs)
        return True;

    def record_output(self, ret, shadow=False, compare_symbolic_shadow_result=False):
        logging.info("RECORDING EFFECT: %s -> %s", self.path.current_constraint, ret)
        #first unify two ret values
        ret_symbolic = ret
        ret_shadow = ret
        ret_shadow_symbolic = ret

        #if return value is a symbolic object, check its mirror and shadow values
        if isinstance(ret, SymbolicObject):
            ret_shadow_symbolic = ret.to_shadow()
            ret_shadow=ret.get_concr_value(shadow=True)
            ret = ret.get_concr_value()
            if (ret != ret_shadow and compare_symbolic_shadow_result and not shadow):
                logging.info("Find a output mismatch: %s vs %s", ret, ret_shadow )

        #if we are running on shadow (old) version, use the shadow return value
        if (shadow):
            ret = ret_shadow
            ret_symbolic = ret_shadow_symbolic
        else:
            #if we are running on the merged version, update mirror and shadow return value for the merged path
            if not self.path.diverge:
                if self.path.current_shadow_constraint.effect is None:
                    self.path.current_shadow_constraint.effect = ret_shadow_symbolic
            if self.path.current_mirror_constraint.effect is None:
                self.path.current_mirror_constraint.effect = ret_symbolic

        #record current constraint's effect
        self.path.current_constraint.effect = ret_symbolic
        self.execution_return_values.append(ret)
        return ret

    def to_dot(self, filename):
        header = "digraph {\n"
        footer = "}\n"
        if self.list_rep is None:
            self.list_rep = self._to_list_rep(self.path.root_constraint)
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

    def to_summary(self, unknown=Symbol('Unknown', INT), shadow = False, mirror = False):
        if self.list_rep is None or shadow or mirror:
            self.list_rep = self._to_list_rep(self.path.root_constraint, shadow, mirror)
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

    def build_smt_from_list (self, nodes, shadow=False, mirror =False):
        if (len(nodes) == 1):
            return self._to_list_rep(nodes[0], shadow)
        else:
            return_list = []
            left_node = nodes.pop(0)
            return_list.append(pred_to_smt(left_node.predicate))
            return_list.append(self._to_list_rep(left_node, shadow, mirror))
            if (len(nodes) >0):
                return_list.append(self.build_smt_from_list(nodes, shadow, mirror))

        return return_list

    def _to_list_rep(self, node, shadow=False, mirror =False):
        if node is None:
            return None
        if shadow:
            children = node.shadow_children
        elif mirror:
            children = node.mirror_children
        else:
            children = node.children
        if ((not shadow) and (not mirror) and node.four_way and len(children) != 0):
            return self.build_smt_from_list(children, shadow, mirror)
        if len(children) == 2:
            if children[0].predicate.symtype.symbolic_eq(children[1].predicate.symtype):
                left = children[0] if children[0].predicate.result else children[1]
                right = children[1] if not children[1].predicate.result else children[0]
                return [pred_to_smt(left.predicate), self._to_list_rep(left, shadow, mirror), self._to_list_rep(right, shadow, mirror)]
            else:
                raise ValueError("Two children of a constraint should have the same predicate!")
        elif len(children) == 1:
            return [pred_to_smt(children[0].predicate), self._to_list_rep(children[0], shadow, mirror), None]
        elif len(children) == 0:
            return node.effect

        raise ValueError("Should not be possible! Can't have more than two children.")
