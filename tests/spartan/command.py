# -*- config: utf-8 -*-
"""
SpartanのEnd-to-Endテストで実行されるコマンド
"""
import json
from argparse import ArgumentParser
from pathlib import Path

FILENAME_TEMPLATE = "a={},b={},_seed={}.json"

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("json", nargs="*")
    parser.add_argument("--a", type=int)
    parser.add_argument("--b", type=str)
    parser.add_argument("--_seed", type=int)
    parser.add_argument("--out_dir", type=str)
    args = parser.parse_args()
    if len(args.json) > 0:
        out_dict = json.loads(args.json[0])
        outpath = Path(out_dict["out_dir"]) / FILENAME_TEMPLATE.format(
            out_dict["a"], out_dict["b"], out_dict["_seed"]
        )
        del out_dict["out_dir"]
    else:
        out_dict = {"a": args.a, "b": args.b, "_seed": args._seed}
        outpath = Path(args.out_dir) / FILENAME_TEMPLATE.format(
            args.a, args.b, args._seed
        )
    with open(outpath, "w") as f:
        json.dump(out_dict, f, sort_keys=True, indent=4)
