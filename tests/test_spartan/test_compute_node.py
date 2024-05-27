# -*- coding: utf-8 -*-
import pytest
from multiprocessing import cpu_count
from queue import Queue
from pathlib import Path

from sekit.spartan import ComputeNode

_interval = 0.001


def test_init() -> None:
    """
    ComputeNodeのコンストラクタでパラメータが適切に設定されるかのテスト
    """
    cn = ComputeNode()
    assert cn.n_jobs == 1
    cn = ComputeNode(n_jobs=4)
    assert cn.n_jobs == 4
    cn = ComputeNode(n_jobs=-1)
    assert cn.n_jobs == cpu_count()

@pytest.mark.parametrize("n_exe", [1, 5, 10])
def test_start(tmp_dir, n_exe) -> None:
    """
    実行したいコマンドが実行されるかのテスト
    touchコマンドでファイルを作り、その数で過不足なく
    実行されているかを確かめる。
    """
    cn = ComputeNode(n_jobs=cpu_count(),
                     interval=_interval)
    out_dir = tmp_dir
    filename_list = [f'___test_{i}' for i in range(n_exe)]
    filepath_list = [out_dir / fn for fn in filename_list]
    commands = [f"touch {fp}" for fp in filepath_list]
    q_commands = Queue()
    for c in commands:
        q_commands.put(c)
    cn.start(q_commands)
    cn.wait_all()
    for filepath in filepath_list:
        assert filepath.is_file()

@pytest.mark.parametrize("device",
                         (['mps'],
                          ['cuda:0', 'cuda:1'])
                         )
def test_device(device,
                tmp_dir):
    """
    GPU等のdeviceの設定をコマンドに付与できるかのテスト.
    TODO: そもそもの構造として、ComputeNodeにこのテストがいるかは要検討.
    ComputeNodeは、与えられたコマンドの実行に専念するべきであり、
    コマンドの修正は行わないほうが良い気がする。
    """
    cn = ComputeNode(n_jobs=3, device=device,
                     interval=_interval)

    here = Path(__file__).parent
    exe = "python " +  str(here / "write_device_info.py ")
    out_dir = tmp_dir
    outpath_list = [str(out_dir / f'device_info_{i}.txt') for i in range(5)]
    commands = [exe + outpath for outpath in outpath_list]
    q_commands = Queue()
    for c in commands:
        q_commands.put(c)
    cn.start(q_commands)
    cn.wait_all()
    for read_path in outpath_list:
        with open(read_path, "r") as f:
            assert f.read() in device
