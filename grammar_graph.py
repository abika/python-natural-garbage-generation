# -*- coding: utf-8 -*-

"""
Syntax graph for language definition used for NLG.

For rule syntax see 'example_res/ger_grammar.txt'.

@author: Alexander Bikadorov
"""

import enum
import random
import itertools
import logging

from myutils import misc_utils


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
            return itertools.chain.from_iterable(
                child.traverse(level + 1) for child in self._child_nodes)

    def __repr__(self):
        return "<Node V:" + str(self.value) + " C:" + str(self._child_nodes) + ">"

    def __str__(self):
        return str(self.value) + "#:" + str(self._child_nodes)


class Literal(Node):
    """End node in graph, representing a syntactic entity."""

    def __init__(self, value):
        super(Literal, self).__init__(value)

    def traverse(self, level):
        yield self.value

    def __repr__(self):
        return "<Literal L:" + str(self.value) + ">"

    def __str__(self):
        return str(self.value) + "|"


class Graph():

    def __init__(self, start_node):
        self._start_node = start_node

    def traverse(self):
        return list(self._start_node.traverse())

    @staticmethod
    def build(gramma_lines):
        """ Build a grammar graph from a list of rules in BNF-like syntax."""

        def get_leaf_node(symbol):
            return nodes_dict.get(symbol, Literal(symbol))

        def parse(elements, greedy, node=None):
            """ Parse one rule line recursive. Anonymous sub nodes are created on the fly"""
            if not elements:
                # were are already at the end
                return None

            current_first = elements.pop(0)

            if current_first == ')':
                # stop aggregation
                return None

            if not node:
                # this is an inner anonymous node
                node = Node()

            if current_first == '(':  # grouping with brackets
                # take all inner elements
                return parse(elements, True, node)

            elif current_first == Operation.or_.value:  # OR: between two choices
                # next element is probability
                p = float(elements.pop(0))
                # parse the two choices
                first = parse(elements, False)
                second = parse(elements, False)
                node.set_edges(Operation.or_, [first, second], p)
            elif current_first == Operation.opt.value:  # OPTIONAL: with or without
                # next element is probability
                p = float(elements.pop(0))
                # parse the optional node
                child = parse(elements, False)
                node.set_edges(Operation.opt, [child], p)
            else:
                if greedy:  # AND: all next nodes combined
                    # consume all children
                    child_nodes = [get_leaf_node(current_first)]
                    while True:
                        next_child = parse(elements, False)
                        if not next_child:
                            break
                        child_nodes.append(next_child)
                    node.set_edges(Operation.and_, child_nodes)

                else:  # standalone symbol: literal or node symbol
                    node = get_leaf_node(current_first)

            return node

        # filter comments
        gramma_rules = [l for l in gramma_lines if l and not l.startswith('#')]
        # split'n'strip symbols and expressions
        symb_expr_list = [tuple(s.strip() for s in l.split('=', 1)) for l in gramma_rules]
        # (only) check for duplicates
        misc_utils.filter_duplicates(symb_expr_list, 0, True)
        logging.debug("input rules: " + str(symb_expr_list))

        # pre-create non-anonymous nodes for later lookup
        nodes_expr_list = [(Node(s), ex) for s, ex in symb_expr_list]

        nodes_dict = dict((node.value, node) for node, _ in nodes_expr_list)

        # set edges
        for node, expr in nodes_expr_list:
            parse(expr.split(), True, node)
            logging.debug("Node: " + str(node) + " ||created from: " + str(expr))

        # start node from first rule
        return Graph(nodes_expr_list[0][0])
