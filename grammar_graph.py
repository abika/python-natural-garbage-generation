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


class Graph(Node):

    @staticmethod
    def build(gramma_rules):
        def get_child_nodes(elements):
            return [nodes_dict.get(child_symb, Literal(child_symb)) for child_symb in elements]

        # create nodes
        symb_expr_list = [l.split('=', 1) for l in gramma_rules]
        nodes_expr_list = [(Node(s.strip()), ex) for s, ex in symb_expr_list]

        # set edges
        nodes_dict = dict((node.value, node) for node, _ in nodes_expr_list)
        for node, expr in nodes_expr_list:
            expr_elements = expr.split()
            op = expr_elements[0]
            if op == Operation.or_.value:
                p = float(expr_elements[1])
                child_nodes = get_child_nodes(expr_elements[2:])
                node.set_edges(Operation.or_, child_nodes, p)
            # default: and operation
            else:
                child_nodes = get_child_nodes(expr_elements[0:])
                node.set_edges(Operation.and_, child_nodes)

        # start node from first rule
        return nodes_expr_list[0][0]
