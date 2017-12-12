# Copyright: copyright.txt

import logging
import inspect
import re
import os
import sys
from .invocation import FunctionInvocation
from .symbolic_types import SymbolicInteger, getSymbolic

# The built-in definition of len wraps the return value in an int() constructor, destroying any symbolic types.
# By redefining len here we can preserve symbolic integer types.
import builtins
builtins.len = (lambda x : x.__len__())

class Loader:
    def __init__(self, filename, entry):
        self._fileName = os.path.basename(filename)
        self._fileName = self._fileName[:-3]
        if (entry == ""):
            self._entryPoint = self._fileName
        else:
            self._entryPoint = entry
        self._resetCallback(True)

    def getFile(self):
        return self._fileName

    def getEntry(self):
        return self._entryPoint
    
    def createInvocation(self):
        inv = FunctionInvocation(self._execute,self._resetCallback)
        func = self.app.__dict__[self._entryPoint]
        argspec = inspect.signature(func)
        # check to see if user specified initial values of arguments
        if "concrete_args" in func.__dict__:
            for (f,v) in func.concrete_args.items():
                if not f in argspec.parameters:
                    raise ImportError("Error in @concrete: " +  self._entryPoint + " has no argument named " + f)
                else:
                    Loader._initializeArgumentConcrete(inv,f,v)
        if "symbolic_args" in func.__dict__:
            for (f,v) in func.symbolic_args.items():
                if not f in argspec.parameters:
                    raise ImportError("Error (@symbolic): " +  self._entryPoint + " has no argument named " + f)
                elif f in inv.getNames():
                    raise ImportError("Argument " + f + " defined in both @concrete and @symbolic")
                else:
                    s = getSymbolic(v)
                    if (s == None):
                        raise ImportError("Error at argument " + f + " of entry point " + self._entryPoint + " : no corresponding symbolic type found for type " + str(type(v)))
                    Loader._initializeArgumentSymbolic(inv, f, s)
        for a in argspec.parameters:
            if not a in inv.getNames():
                Loader._initializeArgumentSymbolic(inv, a, SymbolicInteger)
        return inv

    # need these here (rather than inline above) to correctly capture values in lambda
    def _initializeArgumentConcrete(inv, f, val):
        inv.addArgumentConstructor(f, lambda n: val)

    def _initializeArgumentSymbolic(inv, f, st):
        inv.addArgumentConstructor(f, lambda n: st(None, n))

    def executionComplete(self, return_vals):
        if "expected_result" in self.app.__dict__:
            return self._check(return_vals, self.app.__dict__["expected_result"]())
        if "expected_result_set" in self.app.__dict__:
            return self._check(return_vals, self.app.__dict__["expected_result_set"](),False)
        else:
            logging.info(self._fileName + ".py contains no expected_result function")
            return None

    # -- private

    def _resetCallback(self,firstpass=False):
        self.app = None
        if firstpass and self._fileName in sys.modules:
            raise ImportError("There already is a module loaded named " + self._fileName)
        try:
            if (not firstpass and self._fileName in sys.modules):
                del(sys.modules[self._fileName])
            self.app =__import__(self._fileName)
            if not self._entryPoint in self.app.__dict__ or not callable(self.app.__dict__[self._entryPoint]):
                raise ImportError("File " +  self._fileName + ".py doesn't contain a function named " + self._entryPoint)
        except Exception as arg:
            raise ImportError("Couldn't import " + self._fileName + "\n" + arg)

    def _execute(self, **args):
        return self.app.__dict__[self._entryPoint](**args)

    def _check(self, computed, expected, as_bag=True):
        b_c = _to_bag(computed)
        b_e = _to_bag(expected)
        if as_bag and b_c != b_e or not as_bag and set(computed) != set(expected):
            print("-------------------> %s Test Failed <---------------------" % self._fileName)
            print("Expected: %s, found: %s" % (b_e, b_c))
            return False
        else:
            print("Test Passed <--- %s" % self._fileName)
            return True

def loaderFactory(filename,entry):
    if not os.path.isfile(filename) or not re.search(".py$", filename):
        print("Please provide a Python file to load")
        return None
    try:
        directory = os.path.dirname(filename)
        sys.path = [directory] + sys.path
        ret = Loader(filename, entry)
        return ret
    except ImportError:
        sys.path = sys.path[1:]
        return None

def _to_bag(l):
    bag = {}
    for i in l:
        if i in bag:
            bag[i] += 1
        else:
            bag[i] = 1
    return bag