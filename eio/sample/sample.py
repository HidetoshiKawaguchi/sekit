# -*- coding:utf-8 -*-
import os.path as op
_base = op.join(op.dirname(op.abspath(__file__)), '..', '..')
import sys
sys.path.append(_base)
import pandas as pd

from eio import eio

@eio()
def sample(hidden_layer_sizes: tuple,
           activation: str,
           validation_fraction:float) -> dict:
    dict_out = {
        'a': [a * 2 for a in hidden_layer_sizes],
        'b': '___' + activation + '___',
        'c': validation_fraction * 3
    }
    df_out = pd.DataFrame(
        {
            'a': [hidden_layer_sizes[0]],
            'b': ['___' + activation + '___'],
            'c': [validation_fraction * 3]
        }
    )
    return dict_out, df_out


if __name__ == '__main__':
    sample(hidden_layer_sizes=[100, ],
           activation='relu',
           validation_fraction=0.1)

    sample(hidden_layer_sizes=(200, 300),
           activation='tanh',
           validation_fraction=0.4)
