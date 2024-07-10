# -*- coding: utf-8 -*-
import subprocess
from pathlib import Path
from queue import Queue
from typing import Generator

from sekit.spartan import Cluster, ComputeNode, SshComputeNode

"""
test_ssh_compute_node.pyのコメントに書かれている、テスト環境セットアップ方法を実施した上で実行すること
"""


def test_cluster(
    local_and_ssh_tmp_dir: Generator[Path, None, None], interval: float
) -> None:
    n_made_files = 100
    # ローカルとSSH先の両方で１回以上実行されるくらいの数
    ssh_server_name, tmp_dir_path = local_and_ssh_tmp_dir
    cn = ComputeNode(n_jobs=1, interval=interval)
    scn = SshComputeNode(
        ssh_server_name, n_jobs=1, interval=interval, pre_cmd="source .profile"
    )
    compute_nodes = (cn, scn)
    cluster = Cluster(compute_nodes)
    filepath_list = [tmp_dir_path / f"{i}.txt" for i in range(n_made_files)]
    commands = ["touch " + str(fp) for fp in filepath_list]
    q_commands = Queue()
    for c in commands:
        q_commands.put(c)
    cluster.start(q_commands)
    cluster.wait_all()
    local_flag, ssh_flag = False, False
    for filepath in filepath_list:
        if filepath.exists():
            assert True
            local_flag = True
        else:
            ssh_command = ["ssh", ssh_server_name, "ls", str(filepath)]
            stdout = subprocess.run(
                ssh_command, encoding="utf-8", stdout=subprocess.PIPE
            ).stdout
            assert filepath.name == Path(stdout.rstrip("\n")).name
            ssh_flag = True
    assert local_flag and ssh_flag
