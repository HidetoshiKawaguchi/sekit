# -*- coding: utf-8 -*-
import subprocess
from pathlib import Path
from queue import Queue
from typing import Generator

import pytest

from sekit.spartan import SshComputeNode

"""

"""


def test_init(ssh_server_name: str) -> None:
    """
    SshComputeNodeのコンストラクタでパラメータが適切に設定されるかのテスト
    """
    scn = SshComputeNode(ssh_server_name)
    assert scn.n_jobs == 1
    scn = SshComputeNode(ssh_server_name, n_jobs=4)
    assert scn.n_jobs == 4
    scn = SshComputeNode(ssh_server_name, n_jobs=-1)
    command = ["ssh", ssh_server_name, "grep", "process", "/proc/cpuinfo"]
    result = subprocess.run(command, capture_output=True, text=True)
    n_cpu = len(result.stdout.splitlines())
    assert scn.n_jobs == n_cpu


@pytest.mark.parametrize("n_exe", [1, 5, 10])
def test_start(
    ssh_tmp_dir: Generator[tuple[str, Path], None, None],
    n_exe: int,
    interval: float,
) -> None:
    """
    実行したいコマンドが実行されるかのテスト
    touchコマンドでファイルを作り、その数で過不足なく
    実行されているかを確かめる。
    """
    """
    TODO: test_compute_nodeと処理に共通する部分があるので、
    まとめられないか検討する。
    """
    ssh_server_name, out_dir = ssh_tmp_dir
    scn = SshComputeNode(
        ssh_server_name, interval=interval, pre_cmd="source .profile"
    )
    filename_list = [f"___test_{i}" for i in range(n_exe)]
    filepath_list = [out_dir / fn for fn in filename_list]
    commands = [f"touch {fp}" for fp in filepath_list]
    q_commands = Queue()
    for c in commands:
        q_commands.put(c)
    scn.start(q_commands)
    scn.wait_all()
    for filepath in filepath_list:
        print(str(filepath))
        command = ["ssh", ssh_server_name, "ls", str(filepath)]
        result = subprocess.run(command, capture_output=True, text=True)
        assert result.stdout.splitlines()[0] == str(filepath)


@pytest.mark.parametrize("device", (["mps"], ["cuda:0", "cuda:1"]))
def test_device(
    device: str,
    ssh_tmp_dir: Generator[tuple[str, Path], None, None],
    interval: float,
) -> None:
    """
    TODO: test_compute_nodeと処理に共通する部分があるので、
    まとめられないか検討する。
    """
    # テスト用コンテナにPythonファイルをコピー
    ssh_server_name, tmp_dir = ssh_tmp_dir
    here = Path(__file__).parent
    exe_filepath = str(here / "write_device_info.py")
    scp_command = ["scp", exe_filepath, f"{ssh_server_name}:{tmp_dir}/"]
    subprocess.run(scp_command)

    exe = "python3 " + str(tmp_dir / "write_device_info.py ")
    outpath_list = [str(tmp_dir / f"device_info_{i}.txt") for i in range(5)]
    commands = [exe + outpath for outpath in outpath_list]
    q_commands = Queue()

    scn = SshComputeNode(
        ssh_server_name,
        n_jobs=3,
        interval=interval,
        device=device,
        pre_cmd="source .profile",
    )
    for c in commands:
        q_commands.put(c)
    scn.start(q_commands)
    scn.wait_all()
    for read_path in outpath_list:
        ssh_command = ["ssh", ssh_server_name, "cat", read_path]
        assert (
            subprocess.run(
                ssh_command, encoding="utf-8", stdout=subprocess.PIPE
            ).stdout
            in device
        )
