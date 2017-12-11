# Copyright: see copyright.txt

class FunctionInvocation:
    def __init__(self, function, reset):
        self.function = function
        self.reset = reset
        self.arg_constructor = {}

    def callFunction(self,args):
        self.reset()
        return self.function(**args)

    def addArgumentConstructor(self, name, constructor):
        self.arg_constructor[name] = constructor

    def getNames(self):
        return self.arg_constructor.keys()

    def createArgumentValue(self, name):
        return self.arg_constructor[name](name)

    

