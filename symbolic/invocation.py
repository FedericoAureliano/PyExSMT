# Copyright: see copyright.txt

from contextlib import ExitStack
from mock import patch

class FunctionInvocation:
    def __init__(self, function, reset, module):
        self.module = module
        self.function = function
        self.reset = reset
        self.arg_constructor = {}

    def callFunction(self, args, funcs=[]):
        '''
        ftype1 = FunctionType(INT, [INT, INT])
        f = Symbol("f", ftype1)
        g = Symbol("g", ftype1)
        funcs = [("add", f), ("sub", g)]

        funcs should look like that. List of pairs. 
        Left element is a concrete function
        right element is the symbolic replacement
        '''
        self.reset()
        with ExitStack() as stack:
            [stack.enter_context(patch(self.module+"."+cf, lf)) for cf, lf in funcs]
            ret = self.function(**args)
        return ret

    def addArgumentConstructor(self, name, constructor):
        self.arg_constructor[name] = constructor

    def getNames(self):
        return self.arg_constructor.keys()

    def createArgumentValue(self, name):
        return self.arg_constructor[name](name)
