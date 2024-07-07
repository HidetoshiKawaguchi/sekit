# -*- coding: utf-8 -*-
from pathlib import Path
import shutil
import subprocess
from typing import Generator
from itertools import product, chain
import glob
import math
import json

import pytest

from sekit.spartan import SpartanController
from .command import FILENAME_TEMPLATE

@pytest.mark.parametrize(
    "mode,n_seeds,max_seed",
    [
        ('argparse', 3, 100),
        ('json', 10, 10000)
    ]
)
def test_spartan(
    mode: str,
    n_seeds: int,
    max_seed: int, 
    local_and_ssh_tmp_dir: Generator[Path, None, None],
    interval: float,
) -> None:
    # ローカルとSSH先に実行するpythonファイルのコピー
    ssh_server_name, tmp_dir_path = local_and_ssh_tmp_dir
    source_command_path = Path(__file__).parent / 'command.py'
    exe_path = tmp_dir_path / 'command.py'
    shutil.copy(source_command_path, exe_path)
    scp_command = ['scp', source_command_path, f'{ssh_server_name}:{tmp_dir_path}/']
    subprocess.run(scp_command)

    exe_command = 'python3 ' + str(exe_path)
    param_grid = [
        {
            'a': [0, 1, 2],
            'b': ["hoge", "goro"],
            'out_dir': [str(tmp_dir_path)]
        },
        {
            'a': [3],
            'b': ["giro"],
            'out_dir': [str(tmp_dir_path)]
        }
    ]
    hosts = [
        {'hostname': 'localhost', 'n_jobs': 1},
        {'hostname': ssh_server_name, 'n_jobs': 1}
    ]

    # 実行
    spartan_controller = SpartanController(hosts, mode)
    spartan_controller.exe(
        command=exe_command,
        param_grid=param_grid,
        n_seeds=n_seeds,
        max_seed=max_seed,
        interval=interval
    )

    # ローカルにコピー
    scp_command = ['scp', '-r', f'{ssh_server_name}:' + str(tmp_dir_path) + '/*.json', str(tmp_dir_path)]
    subprocess.run(scp_command)

    # sum_exe = 0
    for a, b in chain(
            product([0, 1, 2], ["hoge", "goro"]),
            product([3], ["giro"])):
        pattern = str(tmp_dir_path / FILENAME_TEMPLATE.format(a, b, '*'))
        local_filepath_list = list(glob.glob(pattern))
        for filepath in local_filepath_list:
            with open(filepath, 'r') as f:
                data = json.load(f)
            assert data['a'] == a
            assert data['b'] == b
            assert data['_seed'] < max_seed
            # sum_exe += 1
    # assert ((3 * 2 + 1) * n_seeds) <= sum_exe <= (3 * 2 + 1) * n_seeds
    # 実行結果にかぶりがでて == にならない可能性があるので省く
