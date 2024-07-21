# -*- coding: utf-8 -*-
import json
import random
from argparse import ArgumentParser


def exe(a: float, b: str, _seed: int) -> str:
    random.seed(_seed)
    s = 0
    c = random.randint(1, 3)
    for _ in range(int(a * (c * 10**8))):
        s += a
    out = "{}-{} (a={}, b={}, _seed={})".format(b, s, a, b, _seed)
    return out


if __name__ == "__main__":
    parser = ArgumentParser(description="")
    parser.add_argument("json", nargs="*")
    parser.add_argument("--a", type=float, default=0.1)
    parser.add_argument("--b", type=str, default="hoge")
    parser.add_argument("--_seed", type=int, default=3939)
    args = parser.parse_args()
    if len(args.json) > 0:
        param = json.loads(args.json[0])
    else:
        param = args.__dict__
        del param["json"]
    print(exe(**param))
