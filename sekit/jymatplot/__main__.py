# -*- coding: utf-8 -*-
import io
import os.path as op
import sys
import time
from argparse import ArgumentParser
from datetime import datetime

import yaml
from .simple_matplot import simple_matplot
from ..utils import load_yaml_or_json


def main():
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", default="")
    parser.add_argument("-o", "--output", default="")
    parser.add_argument("-d", "--display", action="store_true")
    parser.add_argument("--dpi", type=int, default=None)
    args = parser.parse_args()

    if args.input == "":
        in_dict = yaml.safe_load(io.StringIO(sys.stdin.read()))
    else:
        in_dict = load_yaml_or_json(args.input)
    if args.output == "" and args.input != "":
        outpath = op.splitext(op.basename(args.input))[0] + ".png"
    elif args.output != "":
        outpath = args.output
    else:
        outpath = (
            "Plot" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f") + ".png"
        )

    fig = simple_matplot(in_dict, dpi=args.dpi)
    fig.savefig(outpath)
    time.sleep(0.001)

    if args.display:
        print("saved a plot file, " + outpath)


if __name__ == "__main__":
    main()
