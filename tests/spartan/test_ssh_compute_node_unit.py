# -*- coding: utf-8 -*-
import importlib
from types import SimpleNamespace

ssh_module = importlib.import_module("sekit.spartan.SshComputeNode")


def test_init_with_negative_n_jobs_uses_mocked_cpu_count(monkeypatch) -> None:
    monkeypatch.setattr(ssh_module, "getoutput", lambda _: "12")

    compute_node = ssh_module.SshComputeNode("dummy-host", n_jobs=-1)

    assert compute_node.hostname == "dummy-host"
    assert compute_node.n_jobs == 12


def test_start_thread_uses_ssh_thread_without_network(monkeypatch) -> None:
    started_names = []

    def fake_start(self) -> None:
        started_names.append(self.name)

    monkeypatch.setattr(ssh_module.SshComputeNodeThread, "start", fake_start)
    compute_node = ssh_module.SshComputeNode(
        "dummy-host", thread_name="dummy-host"
    )

    compute_node._start_thread(3)

    assert started_names == ["dummy-host_3"]
    assert len(compute_node.threads) == 1


def test_thread_exe_command_builds_ssh_command(monkeypatch) -> None:
    captured = {}

    def fake_popen(cmd, shell):
        captured["cmd"] = cmd
        captured["shell"] = shell
        return SimpleNamespace()

    monkeypatch.setattr(ssh_module, "Popen", fake_popen)
    compute_node = ssh_module.SshComputeNode(
        "dummy-host", pre_cmd="source .profile"
    )
    thread = ssh_module.SshComputeNodeThread(p_cn=compute_node, name="th")
    thread.cmd = "echo hello; echo world"

    thread.exe_command()

    assert captured["shell"] is True
    assert "ssh dummy-host 'source .profile ; echo hello;'" in captured["cmd"]
    assert "ssh dummy-host 'source .profile ;  echo world;'" in captured["cmd"]
