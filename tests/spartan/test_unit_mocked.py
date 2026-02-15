from importlib import import_module
from queue import Queue
from unittest.mock import MagicMock, patch
import typing

if not hasattr(typing, "Self"):
    typing.Self = typing.Any  # type: ignore[attr-defined]

from sekit.spartan.Cluster import Cluster
from sekit.spartan.ComputeNode import ComputeNode
from sekit.spartan.SshComputeNode import SshComputeNode, SshComputeNodeThread

ssh_module = import_module("sekit.spartan.SshComputeNode")


def test_compute_node_start_setup_accepts_iterable() -> None:
    cn = ComputeNode(n_jobs=1)
    cn._start_setup(["echo 1", "echo 2"])

    assert isinstance(cn.q_commands, Queue)
    assert cn.q_commands.qsize() == 2


def test_compute_node_allocate_and_release_device() -> None:
    cn = ComputeNode(device=["cuda:0", "cuda:1"])

    key, allocated = cn.allocate_device()

    assert key == "_device"
    assert allocated == "cuda:0"
    assert cn.device_state[allocated] == 1

    cn.release_device(allocated)
    assert cn.device_state[allocated] == 0


def test_cluster_update_compute_node_changes_interval_and_devices() -> None:
    cn = ComputeNode(n_jobs=1, device=["cuda:0"])
    cluster = Cluster(compute_nodes=[cn], interval=1)

    cluster.update_compute_node(
        hostname="localhost", n_jobs=None, interval=2, devices=["cuda:1"]
    )

    assert cn.n_jobs == 1
    assert list(cn.device_state.keys()) == ["cuda:1"]
    assert cluster.interval == 2


def test_ssh_compute_node_uses_remote_cpu_count_when_n_jobs_minus_one() -> None:
    with patch.object(ssh_module, "getoutput", return_value="8") as mock_getoutput:
        scn = SshComputeNode(hostname="test-ssh-server", n_jobs=-1)

    assert scn.n_jobs == 8
    mock_getoutput.assert_called_once()


def test_ssh_thread_wraps_commands_with_ssh_prefix() -> None:
    mock_proc = MagicMock()

    with patch.object(ssh_module, "Popen", return_value=mock_proc) as mock_popen:
        scn = SshComputeNode(
            hostname="test-ssh-server", pre_cmd="source .profile"
        )
        thread = SshComputeNodeThread(p_cn=scn, name="ssh_thread")
        thread.cmd = "python run.py --x 1; echo done"

        proc = thread.exe_command()

    assert proc is mock_proc
    called_cmd = mock_popen.call_args.args[0]
    assert "ssh test-ssh-server" in called_cmd
    assert "'source .profile ; python run.py --x 1;'" in called_cmd
    assert "'source .profile ;  echo done;'" in called_cmd
    assert mock_popen.call_args.kwargs["shell"] is True
