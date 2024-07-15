#!/usr/bin/env python
# -*- coding: utf-8 -*-
from argparse import ArgumentParser

from ..utils import load_yaml_or_json
from .Spartan import SpartanController

if __name__ == "__main__":
    parser = ArgumentParser(description="")
    parser.add_argument("filepath", help="")
    parser.add_argument("--mode", choices=["argparse", "json"])
    parser.add_argument("--n_seeds", type=int)
    parser.add_argument("--max_size", type=int)
    parser.add_argument("--interval", type=int)
    parser.add_argument("--seed_key")
    parser.add_argument("--max_seed", type=int)
    parser.add_argument("--config_filepath")
    parser.add_argument("--display", type=bool)

    args = parser.parse_args()
    input_dict = load_yaml_or_json(args.filepath)
    hosts = input_dict.get("hosts", [])
    command = input_dict.get("command", "")
    param_grid = input_dict.get("param_grid", [])

    # Option
    option = input_dict.get("option", {})
    mode = option.get("mode", "argparse")
    n_seeds = option.get("n_seeds", 1)
    maxsize = option.get("max_size", 0)
    interval = option.get("interval", 1.0)
    seed_key = option.get("seed_key", "_seed")
    max_seed = option.get("max_seed", 10000000)
    config_filepath = option.get("config_filepath", "")
    display = option.get("display", True)

    # Overwrite command line parameters if setted them.
    for k, v in args.__dict__.items():
        if v is None:
            continue
        v = "'" + v + "'" if isinstance(v, str) else v
        exec("{} = {}".format(k, v))
    sc = SpartanController(hosts, mode=mode)
    sc.exe(
        command,
        param_grid,
        n_seeds=n_seeds,
        maxsize=maxsize,
        interval=interval,
        seed_key=seed_key,
        max_seed=max_seed,
        config_filepath=config_filepath,
        display=display,
    )
