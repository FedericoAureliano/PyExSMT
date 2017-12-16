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
        print("HEY")
        graph = self.get_graph_dict()
        print("HERE", graph)
        dot = self.graph_to_dot(graph)
        print("YO", dot)
        s = Source(dot, filename=filename+".dot", format="png")
        s.view()

    def get_graph_dict(self):
        graph = {} #nodes are keys, edges are elements of the list items
        queue = deque([self.path.root_constraint])
        print("0")
        while len(queue) > 0:
            print("0.5")
            c = queue.popleft()
            if c.predicate is None:
                continue
            queue.extend(c.children)
            rep = c.predicate.symtype.__repr__()
            print("1")
            if not rep in graph:
                print("2")
                #initialize node with no edges out
                graph[rep] = []
            if c.parent is not None:
                print("3")
                prep = c.parent.predicate.symtype.__repr__()
                if c.parent.predicate.result:
                    # if we are the true branch,
                    # add an edge from the parent to this node on the left
                    graph[prep] = [rep] + graph[prep]
                else:
                    graph[prep] = graph[prep]+ [rep]
                if len(graph[prep]) > 2:
                    raise ValueError("%s IS NOT BINARY!!" % prep)
        return graph

    def graph_to_dot(self, graph):
        # print the thing into DOT format
        header = "digraph {\n"
        footer = "\n}\n"
        dot = ""
        for node, edges in graph.items():
            dot += node + " [ label=\"" + node + "\" ];\n"
            for edge in edges:
                dot += node + " -> " + edge + ";\n"
        return header + dot + footer

    def to_summary(self):
        print("\nSUMMARY:")
        for p,e in self.summary:
            print("PATH: %s" % p)
            print("EFFECT: %s\n" % e.__repr__())