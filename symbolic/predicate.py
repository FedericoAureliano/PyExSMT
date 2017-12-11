# Copyright - see copyright.txt

class Predicate:
    """Predicate is one specific ``if'' encountered during the program execution.
       """
    def __init__(self, st, result):
        self.symtype = st
        self.result = result

    def get_vars(self):
        return self.symtype.get_vars()

    def __eq__(self, other):
        if isinstance(other, Predicate):
            res = self.result == other.result and self.symtype.symbolicEq(other.symtype)
            return res
        else:
            return False

    def __hash__(self):
        return hash(self.symtype)

    def __str__(self):
        return "%s (%s)" % (self.symtype, self.result)

    def __repr__(self):
        return self.__str__()

    def negate(self):
        """Negates the current predicate"""
        assert(self.result is not None)
        self.result = not self.result

