#!/usr/bin/python3
# Copyright: see copyright.txt

import os
import sys
import logging
from optparse import OptionParser

from symbolic.loader import *
from symbolic.explore import ExplorationEngine

print("PyExSMT (Python Exploration with SMT)")

sys.path = [os.path.abspath(os.path.join(os.path.dirname(__file__)))] + sys.path

usage = "usage: %prog [options] <path to a *.py file>"
parser = OptionParser(usage=usage)

parser.add_option("-l", "--log", dest="loglevel", action="store", help="Set log level", default="")
parser.add_option("-s", "--start", dest="entry", action="store", help="Specify entry point", default="")
parser.add_option("-g", "--graph", dest="dot_graph", action="store_true", help="Generate a DOT graph of execution tree")
parser.add_option("-m", "--max-iters", dest="max_iters", type="int", help="Run specified number of iterations", default=0)
parser.add_option("--cvc", dest="cvc", action="store_true", help="Use the CVC SMT solver instead of Z3", default=False)
parser.add_option("--z3", dest="cvc", action="store_false", help="Use the Z3 SMT solver")

(options, args) = parser.parse_args()

if options.loglevel in ["info", "INFO", "i", "I"]:
    logging.basicConfig(level=logging.INFO, format='%(message)s')
elif options.loglevel in ["debug", "DEBUG", "d", "D"]:
    logging.basicConfig(level=logging.DEBUG, format='DEBUG:\n%(message)s')

logging.debug("Log Level Set to Debug")

if len(args) == 0 or not os.path.exists(args[0]):
    parser.error("Missing app to execute")
    sys.exit(1)

solver = "cvc" if options.cvc else "z3"

filename = os.path.abspath(args[0])
    
# Get the object describing the application
app = loaderFactory(filename,options.entry)
if app == None:
    sys.exit(1)

print("Exploring " + app.getFile() + "." + app.getEntry())

result = None
try:
    engine = ExplorationEngine(app.createInvocation(), solver=solver)
    generatedInputs, returnVals, path = engine.explore(options.max_iters)
    # check the result
    result = app.executionComplete(returnVals)

    # output DOT graph
    if (options.dot_graph):
        file = open(filename+".dot","w")
        file.write(path.toDot())	
        file.close()

except ImportError as e:
    # createInvocation can raise this
    logging.error(e)
    sys.exit(1)

if result == None or result == True:
    sys.exit(0)
else:
    sys.exit(1)	
