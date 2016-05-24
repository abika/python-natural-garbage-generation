# -*- coding: utf-8 -*-

"""
Syntax graph for language definition used for NLG.

For rule definition see 'example_res/ger_gramma.txt'.

@author: Alexander Bikadorov
"""

import enum
import random
import logging


class Operation(enum.Enum):
    """Branching operation of one node"""
    and_ = '+'
    or_ = '|'
    opt = '['


class Node:
    """One node in graph. Representing a syntax symbol (with value) or an anonymous node inside a
    rule (without value)."""
    def __init__(self, value=None):
        self.value = value
        self._child_nodes = []
        self._p = -1
        self._op = None

    def set_edges(self, op, children, p=-1):
        self._op = op
        self._child_nodes = children
        self._p = p

    def traverse(self, level=0):
        if self._op == Operation.or_:
            rc = 0 if random.random() <= (self._p ** (1.0 / level)) else 1
            return self._child_nodes[rc].traverse(level + 1)
        elif self._op == Operation.opt:
            take = True if random.random() <= (self._p ** (1.0 / level)) else False
            return self._child_nodes[0].traverse(level + 1) if take else []
        else:
            return [child.traverse(level + 1) for child in self._child_nodes]

    def __repr__(self):
        return "<Node V:" + str(self.value) + " C:" + str(self._child_nodes) + ">"

    def __str__(self):
        return str(self.value) + "#:" + str(self._child_nodes)


class Literal(Node):
    """End node in graph, representing a syntactic entity."""

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
        """ Build a grammar graph from a list of rules in BNF-like syntax."""

        def get_child_nodes(elements):
            """ OLD:elements are sub nodes that already exist or literals"""
            return [get_leaf_node(child_symb) for child_symb in elements]

        def get_leaf_node(symbol):
            return nodes_dict.get(symbol, Literal(symbol))

        def parse(elements, greedy, node=None):
            """ Parse one rule line recursive. Anonymous sub nodes are created on the fly"""
            if not node:
                # this is an inner anonymous node
                node = Node()

            current_first = elements.pop(0)
            if current_first == Operation.or_.value: # OR: between two choices
                # next element is probability
                p = float(elements.pop(0))
                # parse the two choices
                first = parse(elements, False)
                second = parse(elements, False)
                node.set_edges(Operation.or_, [first, second], p)
            elif current_first == Operation.opt.value: # OPTIONAL: with or without
                # next element is probability
                p = float(elements.pop(0))
                # parse the optional node
                child = parse(elements, False)
                node.set_edges(Operation.opt, [child], p)
            else:
                if greedy: # AND: all next nodes combined
                    # consume child until end
                    child_nodes = [get_leaf_node(current_first)]
                    while elements:
                        child_nodes.append(parse(elements, False))
                    node.set_edges(Operation.and_, child_nodes)

                else: # standalone symbol: literal or node symbol
                    node = get_leaf_node(current_first)

            return node

        # pre-create non-anonymous nodes for later lookup
        symb_expr_list = [l.split('=', 1) for l in gramma_rules]
        nodes_expr_list = [(Node(s.strip()), ex) for s, ex in symb_expr_list]

        nodes_dict = dict((node.value, node) for node, _ in nodes_expr_list)

        # set edges
        for node, expr in nodes_expr_list:
            parse(expr.split(), True, node)
            logging.debug("Node: " + str(node) + " from : " + str(expr))

        # start node from first rule
        return nodes_expr_list[0][0]
