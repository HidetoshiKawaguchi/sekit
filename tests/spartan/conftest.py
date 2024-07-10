import subprocess
import uuid
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def interval() -> float:
    return 0.001


@pytest.fixture
def ssh_server_name() -> str:
    return "test-ssh-server"


def ssh_mkdir(ssh_server_name: str, dir_path: Path) -> None:
    command = ["ssh", ssh_server_name, "mkdir", str(dir_path)]
    subprocess.run(command)


def ssh_rm_r(ssh_server_name: str, dir_path: Path) -> None:
    command = ["ssh", ssh_server_name, "rm", "-r", str(dir_path)]
    subprocess.run(command)


@pytest.fixture
def ssh_tmp_dir(
    ssh_server_name: str,
) -> Generator[tuple[str, Path], None, None]:
    """
    yieldで返すのは、テスト用SSHサーバーのhostnameと、
    そこで作成された一時ディレクトリを示すパス
    """
    tmp_dir_path = Path() / str(uuid.uuid4())
    ssh_mkdir(ssh_server_name, tmp_dir_path)
    yield ssh_server_name, tmp_dir_path
    ssh_rm_r(ssh_server_name, tmp_dir_path)


@pytest.fixture
def local_and_ssh_tmp_dir(
    ssh_server_name: str, tmp_dir: Generator[Path, None, None]
) -> Generator[tuple[str, Path], None, None]:
    """
    ローカルとSSHサーバの両方に同じ名前のディレクトリを作成して返すディレクトリ
    yieldで返すのは、以下の2つ
    - SSHサーバーのhostname
    - 共通のパス
    """
    tmp_dir_path = tmp_dir
    ssh_mkdir(ssh_server_name, tmp_dir_path)
    yield ssh_server_name, tmp_dir_path
    ssh_rm_r(ssh_server_name, tmp_dir_path)
