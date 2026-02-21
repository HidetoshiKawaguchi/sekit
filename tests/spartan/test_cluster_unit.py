# -*- coding: utf-8 -*-
from queue import Queue

from sekit.spartan import Cluster


class DummyNode:
    def __init__(self, hostname: str) -> None:
        self.hostname = hostname
        self.started_queue = None
        self.kill_all_called = False
        self._remaining_running_checks = 1

    def start(self, queue: Queue) -> None:
        self.started_queue = queue

    def check_continue(self) -> bool:
        if self._remaining_running_checks > 0:
            self._remaining_running_checks -= 1
            return True
        return False

    def kill_all(self) -> None:
        self.kill_all_called = True


def test_cluster_start_and_wait_all_with_mock_nodes() -> None:
    local_node = DummyNode("localhost")
    mock_ssh_node = DummyNode("mock-ssh-host")
    cluster = Cluster((local_node, mock_ssh_node), interval=0)

    cluster.start(["echo 1", "echo 2"])
    cluster.wait_all()

    assert local_node.started_queue is not None
    assert local_node.started_queue is mock_ssh_node.started_queue
    assert cluster.qsize() == 2
    assert local_node.kill_all_called is True
    assert mock_ssh_node.kill_all_called is True
