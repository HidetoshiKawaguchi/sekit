# -*- coding:utf-8 -*-
import os.path as op

_base = op.join(op.dirname(op.abspath(__file__)), "..", "..")
import sys, random, json

sys.path.append(_base)
import pandas as pd

from eio import eio


@eio(out_dir=op.join(_base, "search", "sample", "result"))
def sample(
    hidden_layer_sizes: tuple,
    activation: str,
    validation_fraction: float,
    _seed: int,
) -> dict:
    random.seed(_seed)
    dict_out = {
        "hoge": sum([a * 2 + random.random() for a in hidden_layer_sizes]),
        "goro": "___" + activation + "___",
        "piyo": validation_fraction * 3 + random.random(),
        "giro": [a * 3 + random.random() for a in hidden_layer_sizes],
    }
    return dict_out


if __name__ == "__main__":
    param = json.loads(sys.argv[1])
    sample(**param)
