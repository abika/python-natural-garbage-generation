#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Natural language generation - kind of.



@author: Alexander Bikadorov
"""

import sys
import argparse
import logging
import json

from myutils import file_utils, seq_utils
from grammar_graph import *
from sample_seq import *


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


def main(argv=sys.argv):
    args = _arguments()
    logging.getLogger().setLevel(logging.DEBUG if args.debug else logging.INFO)

    # read gramma rules
    gramma_lines = [l.strip() for l in file_utils.read_file_lines(args.grammar_file)]
    if not gramma_lines:
        logging.warning("no grammar rules for graph")
        return

    # build gramma
    gramma_graph = Graph.build(gramma_lines)
    logging.debug("graph: " + str(gramma_graph))

    # read dictionary
    words_dict = json.loads(file_utils.read_file(args.words_file))
    logging.debug("words_dict: " + str(words_dict))
    sample_dict = {k: SampleSeq(v) for k, v in words_dict.items()}

    for _ in range(args.number):
        # create abstract sentence
        literal_list = gramma_graph.traverse()
        logging.debug("abstract sentence: " + str(literal_list))

        # fill with words
        word_list = [sample_dict[lit].next_rand() for lit in literal_list]
        print(" ".join(seq_utils.join_if(word_list, ',')) + ".")

    logging.debug("DONE!")


if __name__ == "__main__":
    sys.exit(main())
