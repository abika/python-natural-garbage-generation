# -*- coding: utf-8 -*-

"""
Syntax graph for language definition used for NLG.

@author: Alexander Bikadorov
"""

import enum
import random


class Operation(enum.Enum):
    "Branching operation of one node."
    and_ = '+'
    or_ = '|'
    optional = ''


class Node:
    "One node in graph. Representing a syntax symbol"
    def __init__(self, value):
        self.value = value
        self.child_nodes = []
        self.p = -1

    def set_edges(self, op, children, p=-1):
        self.op = op
        self.child_nodes = children
        self.p = p

    def traverse(self, level=0):
        if self.op == Operation.or_:
            rc = 0 if random.random() <= (self.p ** (1.0 / level)) else 1
            return self.child_nodes[rc].traverse(level + 1)
        else:
            return [child.traverse(level + 1) for child in self.child_nodes]

    def __repr__(self):
        return "<Node V:" + str(self.value) + " C:" + str(self.child_nodes) + ">"

    def __str__(self):
        return str(self.value) + "#:" + str(self.child_nodes)


class Literal(Node):
    "End node in graph, representing a syntactic entity."

    def __init__(self, value):
        super(Literal, self).__init__(value)

    def traverse(self, level):
        return self.value

    def __repr__(self):
        return "<Literal L:" + str(self.value) + ">"

    def __str__(self):
        return str(self.value) + "#:" + str(self.child_nodes)
