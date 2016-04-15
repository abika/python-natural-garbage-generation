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
        self._child_nodes = []
        self._p = -1

    def set_edges(self, op, children, p=-1):
        self._op = op
        self._child_nodes = children
        self._p = p

    def traverse(self, level=0):
        if self._op == Operation.or_:
            rc = 0 if random.random() <= (self._p ** (1.0 / level)) else 1
            return self._child_nodes[rc].traverse(level + 1)
        else:
            return [child.traverse(level + 1) for child in self._child_nodes]

    def __repr__(self):
        return "<Node V:" + str(self.value) + " C:" + str(self._child_nodes) + ">"

    def __str__(self):
        return str(self.value) + "#:" + str(self._child_nodes)


class Literal(Node):
    "End node in graph, representing a syntactic entity."

    def __init__(self, value):
        super(Literal, self).__init__(value)

    def traverse(self, level):
        return self.value

    def __repr__(self):
        return "<Literal L:" + str(self.value) + ">"

    def __str__(self):
        return str(self.value) + "|"
