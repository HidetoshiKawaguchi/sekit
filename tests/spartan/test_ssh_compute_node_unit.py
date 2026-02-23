# -*- coding: utf-8 -*-
import importlib
from types import SimpleNamespace
from typing import Protocol

import pytest

ssh_module = importlib.import_module("sekit.spartan.SshComputeNode")


class HasName(Protocol):
    name: str


def test_init_with_negative_n_jobs_uses_mocked_cpu_count(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_getoutput(_: str) -> str:
        return "12"

    monkeypatch.setattr(ssh_module, "getoutput", fake_getoutput)

    compute_node = ssh_module.SshComputeNode("dummy-host", n_jobs=-1)

    assert compute_node.hostname == "dummy-host"
    assert compute_node.n_jobs == 12


def test_start_thread_uses_ssh_thread_without_network(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    started_names: list[str] = []

    def fake_start(self: HasName) -> None:
        started_names.append(self.name)

    monkeypatch.setattr(ssh_module.SshComputeNodeThread, "start", fake_start)
    compute_node = ssh_module.SshComputeNode(
        "dummy-host", thread_name="dummy-host"
    )

    compute_node._start_thread(3)

    assert started_names == ["dummy-host_3"]
    assert len(compute_node.threads) == 1


def test_thread_exe_command_builds_ssh_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_cmd: list[str] = []

    def fake_popen(cmd: list[str]) -> SimpleNamespace:
        nonlocal captured_cmd
        captured_cmd = cmd
        return SimpleNamespace()

    monkeypatch.setattr(ssh_module, "Popen", fake_popen)
    compute_node = ssh_module.SshComputeNode(
        "dummy-host", pre_cmd="source .profile"
    )
    thread = ssh_module.SshComputeNodeThread(p_cn=compute_node, name="th")
    thread.cmd = "echo hello; echo world"

    thread.exe_command()

    assert captured_cmd[0] == "ssh"
    assert captured_cmd[1] == "dummy-host"
    assert "source .profile ; echo hello" in captured_cmd[2]
    assert "source .profile ; echo world" in captured_cmd[2]
    assert " ; ; " not in captured_cmd[2]
