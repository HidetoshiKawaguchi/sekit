# -*- coding: utf-8 -*-
import os
import json, yaml
import random
from queue import Queue
from itertools import product
from time import sleep


from .gen_param import gen_param
from .load_yaml_or_json import load_yaml_or_json
from ._ComputeNode import ComputeNode
from ._SshComputeNode import SshComputeNode
from ._Cluster import Cluster

class SpartanController:
    def __init__(self,
                 hosts=({'hostname': 'localhost',
                         'n_jobs': 1, 'interval': 1}, )):
        compute_nodes = []
        for hst in hosts:
            hostname = hst['hostname']
            n_jobs = hst.get('n_jobs', 1)
            interval = hst.get('interval', 1)
            if hostname == 'localhost':
                cn = ComputeNode(n_jobs=n_jobs,
                                 interval=interval)
            else:
                cn = SshComputeNode(hostname=hostname,
                                    n_jobs=n_jobs,
                                    interval=interval)
            compute_nodes.append(cn)
        self.cluster = Cluster(compute_nodes=compute_nodes)
        self.config_filepath = ''

    def setup_config(self, config_filepath):
        self.config_filepath = config_filepath
        ext = os.path.splitext(os.path.basename(config_filepath))[1]
        initial_config = {'hosts': [
            {'hostname': cn.hostname,
             'n_jobs': cn.n_jobs,
             'interval': cn.interval}
            for cn in self.cluster.compute_nodes
        ]}
        with open(self.config_filepath, 'w') as f:
            if ext == '.json':
                json.dump(initial_config, f)
            else: #yaml
                yaml.dump(initial_config, f)
        self.config_timestamp = os.stat(self.config_filepath).st_mtime

    def update_config(self, display=True):
        try:
            config_dict = load_yaml_or_json(self.config_filepath)
            hosts = config_dict.get('hosts', [])
            for hst in hosts:
                hostname = hst.get('hostname', None)
                if hostname is None:
                    continue
                n_jobs = hst.get('n_jobs', None)
                interval = hst.get('interval', None)
                self.cluster.update_compute_node(hostname,
                                                 n_jobs,
                                                 interval)
            if display:
                print("updated {} config.".format(hostname))
        except Exception as e:
            if display:
                print("coludn't update config.")

    def wait(self, interval=1, display=True):
        sleep(interval)
        if len(self.config_filepath) > 0:
            c_ts = os.stat(self.config_filepath).st_mtime
            if c_ts > self.config_timestamp:
                self.update_config(display=display)
                self.config_timestamp = c_ts

    def exe(self, command, param_grid,
            n_seeds=1, maxsize=0, interval=1.0,
            seed_key='_seed', max_seed=10000000,
            config_filepath='', display=True):
        if len(config_filepath) > 0:
            self.setup_config(config_filepath)
        queue = Queue(maxsize)
        self.cluster.start(queue)
        if param_grid.__class__.__name__ == 'dict':
            param_grid = [param_grid]
        for _, source in product(range(n_seeds), param_grid):
            for param in gen_param(source):
                param[seed_key] = random.randrange(max_seed)
                cmd = command + ' "' \
                      + json.dumps(param).replace('"', '\\"') \
                      + '"'
                if maxsize > 0:
                    while self.cluster.qsize() >= maxsize:
                        self.wait(interval, display=display)
                self.cluster.send_command(cmd)
        while self.cluster.check_continue():
            self.wait(interval, display=display)
        self.cluster.kill_all()
