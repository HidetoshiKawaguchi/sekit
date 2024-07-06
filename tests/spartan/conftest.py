import pytest
import uuid
import subprocess
from pathlib import Path
from typing import Generator

@pytest.fixture
def interval() -> float:
    return 0.001

@pytest.fixture
def ssh_server_name() -> str:
    return 'test-ssh-server'

@pytest.fixture
def ssh_tmp_dir(ssh_server_name: str) -> Generator[tuple[str, Path], None, None]:
    """
    yieldで返すのは、テスト用SSHサーバーのhostnameと、
    そこで作成された一時ディレクトリを示すパス
    """
    tmp_dir_path = Path() / str(uuid.uuid4())
    command = ['ssh', ssh_server_name, 'mkdir', str(tmp_dir_path)]
    subprocess.run(command)
    yield ssh_server_name, tmp_dir_path
    command = ['ssh', ssh_server_name, 'rm', '-r', str(tmp_dir_path)]
    subprocess.run(command)
