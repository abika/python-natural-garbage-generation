#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

@author: Alexander Bikadorov

"""

import random


class SampleSeq:
    """Sampling sequence: Return elements randomly and with low repetitions."""

    def __init__(self, iterable):
        self._sample_order = list(iterable)
        self._sample_pos = 0

    def next_rand(self):
        # shuffle if needed
        if self._sample_pos == 0:
            random.shuffle(self._sample_order)
        # edit counter and return next element
        next_el = self._sample_order[self._sample_pos]
        self._sample_pos = (self._sample_pos + 1) % len(self._sample_order)
        return next_el

    def __repr__(self):
        return "<SampleSeq:" + str(self._sample_order) + " (" + str(self._sample_pos) + ")>"

    def __str__(self):
        return str(self._sample_order) + " (" + str(self._sample_pos) + ")"
