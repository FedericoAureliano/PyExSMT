# Copyright: see copyright.txt

import logging

class Constraint:
    cnt = 0
    """A constraint is a list of predicates leading to some specific
       position in the code."""
    def __init__(self, parent, last_predicate):
        self.inputs = None
        self.predicate = last_predicate
        self.effect = None
        self.processed = False
        self.parent = parent
        self.children = []
        #A list to keep track of child constraints in old (shadow programs)
        self.shadow_children = []
        # A list to keep track of child constraints in new (mirror programs)
        self.mirror_children = []
        self.id = self.__class__.cnt
        self.__class__.cnt += 1
        #A list of sibling nodes from 4 way forking, only init if self is generated by 4 way forking
        self.siblings = None
        #If any of self's child constraint comes from four way forking, set this to True
        self.four_way = False

    def __eq__(self, other):
        """Two Constraints are equal iff they have the same chain of predicates"""
        if isinstance(other, Constraint):
            if not self.predicate == other.predicate:
                return False
            return self.parent is other.parent
        else:
            return False

    def get_asserts_and_query(self , set_processed = True):
        if set_processed:
            self.processed = True
        asserts = self.get_asserts()
        return asserts, self.predicate	       

    def get_asserts(self):
        # collect the assertions
        if self.parent is None:
            return []
        asserts = []
        tmp = self.parent
        while tmp.predicate is not None:
            asserts.append(tmp.predicate)
            tmp = tmp.parent

        return asserts

    def get_length(self):
        if self.parent == None:
            return 0
        return 1 + self.parent.get_length()

    def __str__(self):
        return str(self.predicate) + "  (processed: %s, path_len: %d)" % (self.processed,self.get_length())

    def __repr__(self):
        s = repr(self.predicate) + " (processed: %s)" % (self.processed)
        if self.parent is not None:
            s += "\n  path: %s" % repr(self.parent)
        return s

    def find_child(self, predicate, shadow=False):
        if (shadow):
            children_list = self.shadow_children
        else:
            children_list = self.children

        for c in children_list:
            if predicate == c.predicate:
                return c
        return None

    def add_child(self, predicate, shadow=False, four_way=False):
        if (shadow):
            children_list = self.shadow_children
        else:
            children_list = self.children

        assert(self.find_child(predicate, shadow=shadow) is None)
        c = Constraint(self, predicate)
        children_list.append(c)
        self.four_way = four_way or self.four_way

        return c

    def find_mirror_child(self, predicate):
        children_list = self.mirror_children
        for c in children_list:
            if predicate == c.predicate:
                return c
        return None

    def add_mirror_child(self, predicate):
        children_list = self.mirror_children
        assert (self.find_mirror_child(predicate) is None)
        c = Constraint(self, predicate)
        children_list.append(c)

        return c


    def add_siblings (self, predicate, priority = False):
        if (self.siblings is None):
            self.siblings = []

        if (priority):
            self.siblings.insert(0, predicate)
        else:
            self.siblings.append(predicate)
        return predicate


