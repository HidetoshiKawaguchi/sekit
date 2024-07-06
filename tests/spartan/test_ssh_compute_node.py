# -*- coding: utf-8 -*-
import pytest
import subprocess
from queue import Queue
from pathlib import Path
from typing import Generator

from sekit.spartan import SshComputeNode

"""
テスト環境セットアップ方法
※ 以下の手順のコマンドはすべて本リポジトリのルートディレクトリで実行されるものとする。

1. 例えば以下のコマンドで、SSH接続用の秘密鍵と公開鍵を作る
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
この時、~/.ssh/にid_rsaとid_rsa.pubができる。

2. 以下のコマンドを実行して、このファイルがあるディレクトリにid_rsa.pubを保存する。
cp ~/.ssh/id_rsa.pub ./tests/spartan/

3. 以下のコマンドを実行して、Dockerイメージをビルドする
docker build -t test_ssh_server ./tests/spartan/

4. 以下のコマンドを実行して、テスト用Dockerコンテナを起動する。
docker run -d -p 2222:22 --name test_ssh_container test_ssh_server

5. /etc/hostsを設定してtest-ssh-serverというホスト名で127.0.0.1につながるようにする。
```
127.0.0.1       test-ssh-server
```

6. ~/.ssh/configに以下の設定を追加する。
```
Host test-ssh-server
  HostName test-ssh-server
  User root
  Port 2222
```

確認方法
ssh test-ssh-server
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
    command = ['ssh', ssh_server_name, 'grep', 'process', '/proc/cpuinfo']
    result = subprocess.run(command, capture_output=True, text=True)
    n_cpu = len(result.stdout.splitlines())
    assert scn.n_jobs == n_cpu

@pytest.mark.parametrize("n_exe", [1, 5, 10])
def test_start(ssh_tmp_dir: Generator[tuple[str, Path], None, None],
               n_exe: int,
               interval: float) -> None:
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
    scn = SshComputeNode(ssh_server_name, interval=interval,
                         pre_cmd='source .profile')
    filename_list = [f'___test_{i}' for i in range(n_exe)]
    filepath_list = [out_dir / fn for fn in filename_list]
    commands = [f"touch {fp}" for fp in filepath_list]
    q_commands = Queue()
    for c in commands:
        q_commands.put(c)
    scn.start(q_commands)
    scn.wait_all()
    for filepath in filepath_list:
        print(str(filepath))
        command = ['ssh', ssh_server_name, 'ls', str(filepath)]
        result = subprocess.run(command, capture_output=True, text=True)
        assert result.stdout.splitlines()[0] == str(filepath)

    
@pytest.mark.parametrize("device",
                         (['mps'],
                          ['cuda:0', 'cuda:1'])
                         )
def test_device(device: str,
                ssh_tmp_dir: Generator[tuple[str, Path], None, None],
                interval: float) -> None:
    """
    TODO: test_compute_nodeと処理に共通する部分があるので、
    まとめられないか検討する。
    """
        # テスト用コンテナにPythonファイルをコピー
    ssh_server_name, tmp_dir = ssh_tmp_dir
    here = Path(__file__).parent
    exe_filepath = str(here / 'write_device_info.py')
    scp_command = ['scp', exe_filepath, f'{ssh_server_name}:{tmp_dir}/']
    subprocess.run(scp_command)

    exe = "python3 " + str(tmp_dir / 'write_device_info.py ')
    outpath_list = [str(tmp_dir / f'device_info_{i}.txt') for i in range(5)]
    commands = [exe + outpath for outpath in outpath_list]
    q_commands = Queue()

    scn = SshComputeNode(ssh_server_name,
                         n_jobs=3,
                         interval=interval,
                         device=device,
                         pre_cmd='source .profile')
    for c in commands:
        q_commands.put(c)
    scn.start(q_commands)
    scn.wait_all()
    for read_path in outpath_list:
        ssh_command = ['ssh', ssh_server_name,  'cat', read_path]
        assert subprocess.run(ssh_command, encoding='utf-8',
                              stdout=subprocess.PIPE).stdout in device
