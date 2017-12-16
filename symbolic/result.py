import logging
from graphviz import Source
from collections import deque

from symbolic import pred_to_SMT, get_concr_value
from symbolic.symbolic_types import SymbolicObject

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
        graph = self.get_graph_dict()
        dot = self.dict_to_dot(graph)
        s = Source(dot, filename=filename+".dot", format="png")
        s.view()

    def get_graph_dict(self):
        graph = {} #nodes are keys, edges are elements of the list items
        queue = deque([self.path.root_constraint])
        while len(queue) > 0:
            c = queue.popleft()
            queue.extend(c.children)
            if c.predicate is None:
                rep = "ROOT"
            else:
                rep = c.predicate.symtype.__repr__()
            if not rep in graph:
                #initialize node with no edges out
                graph[rep] = [None, None]
            if c.parent is not None:
                if c.parent.predicate is None:
                    prep = "ROOT"
                    slot = 1
                else:
                    prep = c.parent.predicate.symtype.__repr__()
                    slot = 1 if c.parent.predicate.result else 0
                graph[prep][slot] = rep
        return graph

    def dict_to_dot(self, graph):
        header = "digraph {\n"
        footer = "\n}\n"
        dot = ""
        for node, edges in graph.items():
            dot += "\"" + node + "\" [ label=\"" + node + "\" ];\n"
            for result in range(2):
                edge = edges[result]
                if edge is None:
                    continue
                dot += "\"" + node + "\"  -> " + "\"" + edge + "\" [ label=\"" + str(result) + "\" ];\n"
        return header + dot + footer

    def to_summary(self):
        print("\nSUMMARY:")
        for p, e in self.summary:
            print("PATH: %s" % p)
            print("EFFECT: %s\n" % e.__repr__())
