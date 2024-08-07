#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import sys
from argparse import ArgumentParser

import numpy as np
import pandas as pd

from .stats import stats


def main():
    parser = ArgumentParser(description="")
    # parser.add_argument('csv')
    parser.add_argument("-i", "--input", default="")
    parser.add_argument("-o", "--output", default=sys.stdout)
    parser.add_argument("--separator", default="|")
    parser.add_argument(
        "--funcs",
        nargs="*",
        choices=["ave", "std", "min", "max"],
        default=["ave", "std", "min", "max"],
    )
    parser.add_argument("--ignore", nargs="*", default=("_seed", "_filename"))
    parser.add_argument("--count_key", default="_n")
    parser.add_argument("--n_samples", default=None)

    args = parser.parse_args()

    # TODO:stat_funcsとn_samplesを整える
    func_dict = {
        "ave": ("(ave)", np.average),
        "std": ("(std)", np.std),
        "min": ("(min)", np.min),
        "max": ("(max)", np.max),
    }
    stat_funcs = tuple(func_dict[a] for a in args.funcs)
    n_samples = None if args.n_samples is None else int(args.n_samples)

    in_df = (
        pd.read_csv(io.StringIO(sys.stdin.read()), index_col=0)
        if args.input == ""
        else pd.read_csv(args.input, index_col=0)
    )

    df = stats(
        in_df,
        sep=args.separator,
        ignore=args.ignore,
        count_key=args.count_key,
        stat_funcs=stat_funcs,
        n_samples=n_samples,
    )
    df.to_csv(args.output)


if __name__ == "__main__":
    main()
