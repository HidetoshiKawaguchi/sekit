# -*- coding: utf-8 -*-
from types import SimpleNamespace

import sekit.spartan.Spartan as spartan_module


def test_controller_builds_remote_node_without_ssh_access(monkeypatch) -> None:
    created = {"compute": [], "ssh": []}

    class DummyComputeNode:
        def __init__(self, n_jobs=1, interval=1, device=None) -> None:
            self.hostname = "localhost"
            self.n_jobs = n_jobs
            self.interval = interval
            self.device_state = {d: 0 for d in (device or [])}
            created["compute"].append(self)

    class DummySshComputeNode:
        def __init__(self, hostname, n_jobs=1, interval=1, device=None) -> None:
            self.hostname = hostname
            self.n_jobs = n_jobs
            self.interval = interval
            self.device_state = {d: 0 for d in (device or [])}
            created["ssh"].append(self)

    class DummyCluster:
        def __init__(self, compute_nodes) -> None:
            self.compute_nodes = compute_nodes

    monkeypatch.setattr(spartan_module, "ComputeNode", DummyComputeNode)
    monkeypatch.setattr(spartan_module, "SshComputeNode", DummySshComputeNode)
    monkeypatch.setattr(spartan_module, "Cluster", DummyCluster)

    controller = spartan_module.SpartanController(
        hosts=[
            {"hostname": "localhost", "n_jobs": 1},
            {"hostname": "mock-ssh-host", "n_jobs": 2},
        ]
    )

    assert isinstance(controller.cluster, DummyCluster)
    assert len(created["compute"]) == 1
    assert len(created["ssh"]) == 1
    assert created["ssh"][0].hostname == "mock-ssh-host"
    assert controller.make_param_str({"a": 1}) == "--a 1"


def test_controller_json_mode_uses_json_serializer(monkeypatch) -> None:
    monkeypatch.setattr(
        spartan_module, "Cluster", lambda compute_nodes: SimpleNamespace()
    )
    monkeypatch.setattr(
        spartan_module,
        "ComputeNode",
        lambda n_jobs=1, interval=1, device=None: SimpleNamespace(
            hostname="localhost",
            n_jobs=n_jobs,
            interval=interval,
            device_state={},
        ),
    )

    controller = spartan_module.SpartanController(mode="json")

    assert controller.make_param_str({"a": 1}) == '"{\\"a\\": 1}"'
