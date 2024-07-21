# -*- coding: utf-8 -*-
import json
import os
import random
from itertools import product
from queue import Queue
from time import sleep
from typing import Any, Sequence

import yaml

from ..utils import load_yaml_or_json
from .Cluster import Cluster
from .ComputeNode import ComputeNode
from .gen_param import gen_param
from .SshComputeNode import SshComputeNode


def _make_json_str(param: dict[str, Any]) -> str:
    return '"' + json.dumps(param).replace('"', '\\"') + '"'


def _make_argparse_str(param: dict[str, Any]) -> str:
    return " ".join("--{} {}".format(k, v) for k, v in param.items())


class SpartanController:
    def __init__(
        self,
        hosts: Sequence[dict[str, int | float | str]] | None = None,
        mode: str = "argparse",
    ) -> None:
        if hosts is None:
            hosts = ({"hostname": "localhost", "n_jobs": 1, "interval": 1},)
        compute_nodes = []
        for hst in hosts:
            hostname = hst["hostname"]
            n_jobs = hst.get("n_jobs", 1)
            interval = hst.get("interval", 1)
            device = hst.get("device", [])
            if hostname == "localhost":
                cn = ComputeNode(
                    n_jobs=n_jobs, interval=interval, device=device
                )
            else:
                cn = SshComputeNode(
                    hostname=hostname,
                    n_jobs=n_jobs,
                    interval=interval,
                    device=device,
                )
            compute_nodes.append(cn)
        self.cluster = Cluster(compute_nodes=compute_nodes)
        self.config_filepath = ""
        self.make_param_str = {
            "argparse": _make_argparse_str,
            "json": _make_json_str,
        }[mode.lower()]

    def setup_config(self, config_filepath: str) -> None:
        self.config_filepath = config_filepath
        ext = os.path.splitext(os.path.basename(config_filepath))[1]
        initial_config = {
            "hosts": [
                {
                    "hostname": cn.hostname,
                    "n_jobs": cn.n_jobs,
                    "interval": cn.interval,
                    "device": list(cn.device_state.keys()),
                }
                for cn in self.cluster.compute_nodes
            ]
        }
        with open(self.config_filepath, "w") as f:
            if ext == ".json":
                json.dump(initial_config, f)
            else:  # yaml
                yaml.dump(initial_config, f)
        self.config_timestamp = os.stat(self.config_filepath).st_mtime

    def update_config(self, display: bool = True) -> None:
        try:
            config_dict = load_yaml_or_json(self.config_filepath)
            hosts = config_dict.get("hosts", [])
            for hst in hosts:
                hostname = hst.get("hostname", None)
                if hostname is None:
                    continue
                n_jobs = hst.get("n_jobs", None)
                interval = hst.get("interval", None)
                devices = hst.get("device", None)
                self.cluster.update_compute_node(
                    hostname, n_jobs, interval, devices
                )
            if display:
                print("updated {} config.".format(hostname))
        except Exception:
            if display:
                print("coludn't update config.")

    def wait(self, interval: int | float = 1, display: bool = True):
        sleep(interval)
        if len(self.config_filepath) > 0:
            c_ts = os.stat(self.config_filepath).st_mtime
            if c_ts > self.config_timestamp:
                self.update_config(display=display)
                self.config_timestamp = c_ts

    def exe(
        self,
        command: str,
        param_grid: list[dict[str, Any]] | dict[str, Any],
        n_seeds: int = 1,
        maxsize: int = 0,
        interval: int | float = 1.0,
        seed_key: str = "_seed",
        max_seed: int = 10000000,
        config_filepath: str = "",
        display: bool = True,
    ) -> None:
        if len(config_filepath) > 0:
            self.setup_config(config_filepath)
        queue = Queue(maxsize)
        self.cluster.start(queue)
        if param_grid.__class__.__name__ == "dict":
            param_grid = [param_grid]
        for _, source in product(range(n_seeds), param_grid):
            for param in gen_param(source):
                param[seed_key] = random.randrange(max_seed)
                cmd = command + " " + self.make_param_str(param)
                if maxsize > 0:
                    while self.cluster.qsize() >= maxsize:
                        self.wait(interval, display=display)
                self.cluster.send_command(cmd)
        while self.cluster.check_continue():
            self.wait(interval, display=display)
        self.cluster.kill_all()
