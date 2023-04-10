# -*- coding: utf-8 -*-
from time import sleep
from queue import Queue

from ._ComputeNode import ComputeNode
from ._SshComputeNode import SshComputeNode

class Cluster():
    def __init__(self,
                 compute_nodes=[ComputeNode(), ],
                 interval=1):
        self.compute_nodes = compute_nodes
        self.interval = interval
        self.commands_queue = None


    def _start_setup(self, commands):
        if type(commands) == Queue:
            # Queueならそれを入れる
            self.commands_queue = commands
        elif hasattr(commands, '__iter__'):
            # QueueではくてイテレーションするならQueueを**新しく**作る
            self.commands_queue = Queue()
            for c in commands:
                self.commands_queue.put(c)
        else:
            raise TypeError('Queue型もしくはイテレーション型を入れてください')

    def start(self, commands):
        self._start_setup(commands)
        for hst in self.compute_nodes:
            hst.start(self.commands_queue)

    def check_continue(self):
        return any(hst.check_continue() for hst in self.compute_nodes)

    def wait_all(self):
        while self.check_continue():
            sleep(self.interval)
        self.kill_all()

    def kill_all(self):
        for hst in self.compute_nodes:
            hst.kill_all()

    def send_command(self, command):
        self.commands_queue.put(command)

    def qsize(self):
        return self.commands_queue.qsize()

    def search_conpute_node(self, hostname):
        for cn in self.compute_nodes:
            if cn.hostname == hostname:
                return cn

    def update_compute_node(self, hostname,
                            n_jobs=None, interval=None, devices=None):
        compute_node = self.search_conpute_node(hostname)
        if type(n_jobs).__name__ == 'int':
            compute_node.change_n_jobs(n_jobs)
        if type(interval).__name__ == 'int':
            self.interval = interval
        if hasattr(devices, '__iter__'):
            if all(type(d).__name__ == 'str' for d in devices):
                compute_node.change_device_state(devices)









