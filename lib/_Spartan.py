# -*- coding: utf-8 -*-
import json
import random
from queue import Queue
from itertools import product


from .gen_param import gen_param
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

    def exe(self, command, param_grid,
            n_seeds=1, maxsize=0,
            seed_key='_seed', max_seed=10000000):
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
                queue.put(cmd)
        self.cluster.wait_all()
