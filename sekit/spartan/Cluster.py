# -*- coding: utf-8 -*-
from collections.abc import Iterable
from queue import Queue
from time import sleep
from typing import Sequence, cast

from .ComputeNode import ComputeNode


class Cluster:
    def __init__(
        self,
        compute_nodes: Sequence[ComputeNode] | None = None,
        interval: int | float = 1,
    ) -> None:
        if compute_nodes is None:
            self.compute_nodes = [
                ComputeNode(),
            ]
        else:
            self.compute_nodes = list(compute_nodes)
        self.interval = interval
        self.commands_queue: Queue[str] | None = None

    def _start_setup(self, commands: Iterable[str] | Queue[str]) -> None:
        if isinstance(commands, Queue):
            # Queueならそれを入れる
            self.commands_queue = commands
        elif hasattr(commands, "__iter__"):
            # QueueではくてイテレーションするならQueueを**新しく**作る
            self.commands_queue = Queue()
            for c in commands:
                self.commands_queue.put(c)
        else:
            raise TypeError("Queue型もしくはイテレーション型を入れてください")

    def start(self, commands: Iterable[str] | Queue[str]) -> None:
        self._start_setup(commands)
        for hst in self.compute_nodes:
            hst.start(cast(Queue[str], self.commands_queue))

    def check_continue(self) -> bool:
        return any(hst.check_continue() for hst in self.compute_nodes)

    def wait_all(self) -> None:
        while self.check_continue():
            sleep(self.interval)
        self.kill_all()

    def kill_all(self) -> None:
        for hst in self.compute_nodes:
            hst.kill_all()

    def send_command(self, command: str) -> None:
        cast(Queue[str], self.commands_queue).put(command)

    def qsize(self) -> int:
        return cast(Queue[str], self.commands_queue).qsize()

    def search_conpute_node(self, hostname: str) -> ComputeNode:
        for cn in self.compute_nodes:
            if cn.hostname == hostname:
                return cn
        raise ValueError("ComputeNode {} が見つかりません".format(hostname))

    def update_compute_node(
        self,
        hostname: str,
        n_jobs: int | None = None,
        interval: int | float | None = None,
        devices: Iterable[str] | None = None,
    ) -> None:
        compute_node = self.search_conpute_node(hostname)
        if isinstance(n_jobs, int):
            compute_node.change_n_jobs(n_jobs)
        if isinstance(interval, (int, float)):
            self.interval = interval
        if isinstance(devices, Iterable):
            device_list = list(devices)
            if all(isinstance(d, str) for d in device_list):
                compute_node.change_device_state(device_list)
