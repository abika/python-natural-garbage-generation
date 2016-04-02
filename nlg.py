#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Created on Thu Mar 31 16:10:53 2016

@author: Alexander Bikadorov
"""

import sys
import argparse
import logging

import _myutils

import random
import json


#class GrammaGraph:
    #def __init__(self, root):
        #self.root = root


class Node:
    def __init__(self, value, children=[]):
        self.value = value
        self.child_nodes = children

    def traverse(self):
        return self.value if not self.child_nodes else [child.traverse() for child in self.child_nodes]

    def __repr__(self):
        v = str(self.value)
        return "<EndNode L:" + v + ">" if not self.child_nodes else "<Node V:" + v + " C:" + str(self.child_nodes) + ">"

    def __str__(self):
        return str(self.value) + "#:" + str(self.child_nodes)


def _arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', help='enable debug output')
    parser.add_argument('grammar_file', metavar='grammar-file', type=str, help='plain text file containing grammar in simple BNF form')
    parser.add_argument('words_file', metavar='words-file', type=str, help='word list file for all syntax literals in JSON format')
    return parser.parse_args()


def _build_gramma_graph(gramma_lines):
    def rec_builder(symb, gramma_dict):
        #head, *tail = lines
        if symb not in gramma_dict:
            # leaf (or recursive!)
            return Node(symb)

        expr = gramma_dict.pop(symb)
        and_symbols = expr.split()
        #logging.debug("building node: " + symb + " := " + str(and_symbols))
        #gen = (cs for cs in and_symbols if cs in gramma_dict)
        childs = [rec_builder(child_symb, gramma_dict) for child_symb in and_symbols]

        return Node(symb, childs)

    symb_exp_list = [l.split('=', 1) for l in gramma_lines]
    symb_exp_list = [(s.strip(), ex.strip()) for s, ex in symb_exp_list]
    gramma_dict = dict(symb_exp_list)
    logging.debug("gramma dict: " + str(gramma_dict))

    if not symb_exp_list:
        logging.warning("no gramma rules")
        return

    start_symb = symb_exp_list[0][0].strip()

    root_node = rec_builder(start_symb, gramma_dict)
    return root_node


def _create_abstr_sentence(gramma_graph):
    return _myutils.flatten(gramma_graph.traverse())


def main(argv=sys.argv):
    args = _arguments()
    logging.getLogger().setLevel(logging.DEBUG if args.debug else logging.INFO)

    gramma_lines = [l.strip() for l in _myutils.read_file_lines(args.grammar_file)]
    gramma_lines = [l for l in gramma_lines if l and not l.startswith('#')]
    logging.debug("gramma read: " + str(gramma_lines))

    # load gramma
    gramma_graph = _build_gramma_graph(gramma_lines)
    logging.info("graph: " + str(gramma_graph))

    # build abstract sentence
    literal_list = _create_abstr_sentence(gramma_graph)
    logging.info("abstract sentence: " + str(literal_list))

    words_dict = json.loads(_myutils.read_file(args.words_file))
    logging.debug("words_dict: " + str(words_dict))

    word_list = [random.choice(words_dict[lit]) for lit in literal_list]
    logging.info("sentence: " + " ".join(word_list) + ".")

    logging.debug("DONE!")


if __name__ == "__main__":
    sys.exit(main())
