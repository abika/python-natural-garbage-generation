#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""


Created on Thu Mar 31 16:10:53 2016

@author: Alexander Bikadorov
"""

import sys
import argparse
import logging

import random
import json

import _myutils
from grammar_graph import *


def _arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true',
        help='enable debug output')
    parser.add_argument('-n', '--number', default=10, metavar='grammar-file',
        type=str, help='number of sentences to generate')
    parser.add_argument('grammar_file', metavar='grammar-file', type=str,
        help='plain text file containing grammar in simple BNF form')
    parser.add_argument('words_file', metavar='words-file', type=str,
        help='word list file for all syntax literals in JSON format')
    return parser.parse_args()


def _build_gramma_graph(gramma_rules):
    def get_child_nodes(elements):
        return [nodes_dict.get(child_symb, Literal(child_symb)) for child_symb in elements]

    if not gramma_rules:
        logging.warning("no gramma rules for graph")
        return

    # create nodes
    symb_expr_list = [l.split('=', 1) for l in gramma_rules]
    nodes_expr_list = [(Node(s.strip()), ex) for s, ex in symb_expr_list]

    # set edges
    nodes_dict = dict((node.value, node) for node, _ in nodes_expr_list)
    for node, expr in nodes_expr_list:
        expr_elements = expr.split()
        logging.debug("set: " + str(node) + " := " + str(expr_elements))
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


def _create_abstr_sentence(gramma_graph):
    return _myutils.flatten(gramma_graph.traverse())


def main(argv=sys.argv):
    args = _arguments()
    logging.getLogger().setLevel(logging.DEBUG if args.debug else logging.INFO)

    gramma_lines = [l.strip() for l in _myutils.read_file_lines(args.grammar_file)]
    gramma_lines = [l for l in gramma_lines if l and not l.startswith('#')]
    logging.debug("gramma read: " + str(gramma_lines))

    random.seed()

    # load gramma
    gramma_graph = _build_gramma_graph(gramma_lines)
    logging.info("graph: " + str(gramma_graph))

    words_dict = json.loads(_myutils.read_file(args.words_file))
    logging.debug("words_dict: " + str(words_dict))

    for _ in range(args.number):
        # build abstract sentence
        literal_list = _create_abstr_sentence(gramma_graph)
        logging.info("abstract sentence: " + str(literal_list))

        # fill with words
        word_list = [random.choice(words_dict[lit]) for lit in literal_list]
        logging.info("sentence: " + " ".join(word_list) + ".")

    logging.debug("DONE!")


if __name__ == "__main__":
    sys.exit(main())
