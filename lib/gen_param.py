# -*- coding: utf-8 -*-
import random
from itertools import product

def gen_param(source):
    if type(source) is dict:
        source = source.items()
    keys = tuple(v[0] for v in source)
    values = (v[1] for v in source)
    for v in product(*values):
        yield {keys[index]:value for index, value in enumerate(v)}

