#!/usr/bin/python3
# Copyright: see copyright.txt

import os
import sys
import logging
from argparse import ArgumentParser
import re

from symbolic import parse_types, uninterp_func_pair
from symbolic.loader import *
from symbolic.explore import ExplorationEngine

from pysmt.shortcuts import *

print("PyExSMT (Python Exploration with SMT)")

sys.path = [os.path.abspath(os.path.join(os.path.dirname(__file__)))] + sys.path

parser = ArgumentParser()

parser.add_argument("--log", dest="loglevel", action="store", \
                                help="Set log level", default="")
parser.add_argument('--uninterp', dest="uninterp", nargs=3, \
                                metavar=('name', 'return_type', 'arg_types'), \
                                help='<func_name> <return_type> <arg_types>')
parser.add_argument("--entry", dest="entry", action="store", \
                                help="Specify entry point", default="")
parser.add_argument("--graph", dest="dot_graph", action="store_true", \
                                help="Generate a DOT graph of execution tree")
parser.add_argument("--summary", dest="summary", action="store_true", \
                                help="Generate a functional summary")
parser.add_argument("--max-iters", dest="max_iters", type=int, \
                                help="Limit number of iterations", default=0)
parser.add_argument("--max-depth", dest="max_depth", type=int, \
                                help="Limit the depth of paths", default=0)
parser.add_argument("--solver", dest="solver", action="store", \
                                help="Choose SMT solver", default="z3")
parser.add_argument(dest="file", action="store", help="Select Python file")

options = parser.parse_args()


if options.loglevel in ["info", "INFO", "i", "I"]:
    logging.basicConfig(level=logging.INFO, format='%(message)s')
elif options.loglevel in ["debug", "DEBUG", "d", "D"]:
    logging.basicConfig(level=logging.DEBUG, format='DEBUG:\t%(message)s')
elif options.loglevel == "":
    pass
else:
    logging.error("Unrecognized Log Level")
    sys.exit(-1)

logging.debug("Log Level Set to Debug")

if options.file == "" or not os.path.exists(options.file):
    parser.error("Missing app to execute")
    sys.exit(1)

if not options.solver in get_env().factory.all_solvers(): 
    logging.error("Solver %s not available" % options.solver)
    sys.exit(-1)
else:
    solver = options.solver

summary = options.summary

filename = os.path.abspath(options.file)
    
# Get the object describing the application
app = loaderFactory(filename,options.entry)
if app == None:
    sys.exit(1)

print("Exploring " + app.getFile() + "." + app.getEntry())

funcs = uninterp_func_pair(options.uninterp, app.getFile())

result = None
try:
    engine = ExplorationEngine(app.createInvocation(), solver=solver)
    result_struct = engine.explore(options.max_iters, options.max_depth, funcs)

    return_vals = result_struct.execution_return_values

    # check the result
    result = app.executionComplete(return_vals)

    # print summary
    if summary:
        summary = result_struct.to_summary()
        print("\nSummary:\n%s\n" % summary)

    # output DOT graph
    if options.dot_graph:
        result_struct.to_dot(filename)

except ImportError as e:
    # createInvocation can raise this
    logging.error(e)
    sys.exit(1)

except NotImplementedError as e:
    # Some operators are not implemented.
    # Don't need a stack trace for this.
    logging.error(e)
    sys.exit(1)

except TypeError as e:
    # Some operators are not implemented.
    # Don't need a stack trace for this.
    logging.error(e)
    sys.exit(1)

if result is None or result:
    sys.exit(0)
else:
    sys.exit(1)
