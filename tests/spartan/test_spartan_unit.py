# -*- coding: utf-8 -*-
from types import SimpleNamespace
from typing import Any

import pytest

import sekit.spartan.Spartan as spartan_module


def test_controller_builds_remote_node_without_ssh_access(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    created: dict[str, list[Any]] = {"compute": [], "ssh": []}

    class DummyComputeNode:
        def __init__(
            self,
            n_jobs: int = 1,
            interval: int | float = 1,
            device: list[str] | None = None,
        ) -> None:
            self.hostname = "localhost"
            self.n_jobs = n_jobs
            self.interval = interval
            self.device_state = {d: 0 for d in (device or [])}
            created["compute"].append(self)

    class DummySshComputeNode:
        def __init__(
            self,
            hostname: str,
            n_jobs: int = 1,
            interval: int | float = 1,
            device: list[str] | None = None,
        ) -> None:
            self.hostname = hostname
            self.n_jobs = n_jobs
            self.interval = interval
            self.device_state = {d: 0 for d in (device or [])}
            created["ssh"].append(self)

    class DummyCluster:
        def __init__(self, compute_nodes: list[Any]) -> None:
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


def test_controller_json_mode_uses_json_serializer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def make_dummy_cluster(compute_nodes: list[Any]) -> SimpleNamespace:
        return SimpleNamespace(compute_nodes=compute_nodes)

    def make_dummy_compute_node(
        n_jobs: int = 1,
        interval: int | float = 1,
        device: list[str] | None = None,
    ) -> SimpleNamespace:
        return SimpleNamespace(
            hostname="localhost",
            n_jobs=n_jobs,
            interval=interval,
            device_state={d: 0 for d in (device or [])},
        )

    monkeypatch.setattr(spartan_module, "Cluster", make_dummy_cluster)
    monkeypatch.setattr(
        spartan_module,
        "ComputeNode",
        make_dummy_compute_node,
    )

    controller = spartan_module.SpartanController(mode="json")

    assert controller.make_param_str({"a": 1}) == '"{\\"a\\": 1}"'
