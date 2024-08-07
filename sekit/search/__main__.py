#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from argparse import ArgumentParser

import pandas as pd

from .search import search


def main():
    parser = ArgumentParser(description="")
    parser.add_argument("filepath", nargs="*")
    parser.add_argument("--dir", default=None)
    parser.add_argument("--display", action="store_true")
    parser.add_argument("-o", "--output", default=sys.stdout)
    parser.add_argument("--param_key", default="_param")
    parser.add_argument("--filename_key", default="_filename")
    parser.add_argument("--head_columns", nargs="*", default=["_header"])
    parser.add_argument(
        "--tail_columns", nargs="*", default=["_process_time", "_filename"]
    )
    parser.add_argument("--separator", default="|")
    parser.add_argument("--cache", default=None)
    args = parser.parse_args()

    target_df = None if args.cache is None else pd.read_csv(args.cache)
    df = search(
        args.filepath,
        dir=args.dir,
        display=args.display,
        param_key=args.param_key,
        filename_key=args.filename_key,
        sep=args.separator,
        head_columns=args.head_columns,
        tail_columns=args.tail_columns,
        target_df=target_df,
    )
    df.to_csv(args.output)


if __name__ == "__main__":
    main()
