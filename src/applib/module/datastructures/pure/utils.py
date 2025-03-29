"""Courtesy of https://opendatastructures.org/"""

import numpy


def new_array(n, dtype=object):
    return numpy.empty(n, dtype)
