# -*- coding: utf-8 -*-
import pytest
import os
import shutil
from pathlib import Path
import json
from typing import Callable, Generator
import numpy as np

import pandas as pd
from sekit.utils import support_numpy
from sekit.eio import eio


@pytest.fixture
def param() -> dict[str, list[int] | str | float | int]:
    return {
        'hidden_layer_sizes': [100, 200],
        'activation':'relu',
        'validation_fraction':0.1,
        '_seed': 2525
    }


@pytest.fixture
def filenames() -> list[str]:
    return [
        'sample,a=relu,hls=100_200,vf=0.1,_s=2525.json',
        'sample,a=relu,hls=100_200,vf=0.1,_s=2525.csv',
        'sample,a=relu,hls=100_200,vf=0.1,_s=2525_1.json',
        'sample,a=relu,hls=100_200,vf=0.1,_s=2525_1.csv',
        'sample,a=relu,hls=100_200,vf=0.1,_s=2525_2.csv'
    ]

@pytest.fixture
def made_dir_name() -> str:
    return 'made_dir'

    

def make_sample(out_dir: str = './',
                header: str | None = None,
                param_flag: bool = True,
                header_flag: bool = True,
                process_time: bool = True,
                trace_back: bool =False,
                display: bool = True,
                error_display: bool = False,
                sort_keys: bool = True,
                ensure_ascii: bool = False,
                mkdir: str = 'off',
                indent: int = 4,
                default: Callable[[np.float32 | np.int64 | np.ndarray], float | int | list[int | float]] = support_numpy,
                tail_param: tuple[str] = ('_seed', )
                ) -> Callable[
                    [list[int], str, float, int],
                    tuple[dict, pd.DataFrame, dict, pd.DataFrame, pd.DataFrame]
                ]:
    @eio(out_dir=out_dir, header=header, param_flag=param_flag, header_flag=header_flag,
         process_time=process_time, trace_back=trace_back,
         display=display, error_display=error_display,
         sort_keys=sort_keys, ensure_ascii=ensure_ascii,
         mkdir=mkdir,
         indent=indent, default=support_numpy, tail_param=tail_param)
    def sample(hidden_layer_sizes: tuple,
               activation: str,
               validation_fraction:float,
               _seed:int) -> tuple[dict, pd.DataFrame, dict, pd.DataFrame, pd.DataFrame]:
        dict_out = {
            'a': [a * 2 for a in hidden_layer_sizes],
            'b': '___' + activation + '___',
            'c': validation_fraction * 3
        }
        df_out = pd.DataFrame(
            {
                'a': [hidden_layer_sizes[0]],
                'b': ['___' + activation + '___'],
                'c': [validation_fraction * 3]
            }
        )
        return dict_out, df_out, dict_out, df_out, df_out
    return sample



def assert_json(result: dict[str, dict[str, list[int] | str | float]]) -> None:
    assert result['a'][0] == 200
    assert result['a'][1] == 400
    assert result['b'] == '___relu___'
    assert result['c'] == pytest.approx(0.3)
    assert result['_param']['hidden_layer_sizes'][0] == 100
    assert result['_param']['hidden_layer_sizes'][1] == 200
    assert result['_param']['activation'] == 'relu'
    assert result['_param']['validation_fraction'] == 0.1
    assert result['_param']['_seed'] == 2525

def assert_df(df: pd.DataFrame) -> None:
    assert df['a'][0] == 100
    assert df['b'][0] == '___relu___'
    assert df['c'][0] == pytest.approx(0.3)

def assert_eio(*args: list[Path]) -> None:
    for filepath in args:
        ext = os.path.splitext(filepath)[1]
        if ext == 'json':
            with open(file_path, 'r') as f:
                so = json.load(f)
                assert_json(so)
        elif ext == 'csv':
            assert_df(pd.read_csv(file_path))


def test_eio_smoke(param: dict[str, list[int] | str | float | int],
                   filenames: list[str],
                   tmp_dir: Generator[Path, None, None]) -> None:
    out_dir = tmp_dir
    sample = make_sample(out_dir=out_dir, display=False)
    sample(**param)
    paths = [out_dir / filename for filename in filenames]
    assert_eio(*paths)


    
def test_eio_mkdir_on(param: dict[str, list[int] | str | float | int],
                      filenames: list[str],
                      made_dir_name: str,
                      tmp_dir: Generator[Path, None, None]) -> None:
    out_dir = tmp_dir
    mk_dir_path = out_dir /  made_dir_name

    # on
    func = make_sample(out_dir=mk_dir_path,
                       display=False, mkdir='on')
    paths = [out_dir / filename for filename in filenames]
    func(**param)
    assert_eio(*paths)


def test_eio_mkdir_shallow(param: dict[str, list[int] | str | float | int],
                           filenames: list[str],
                           made_dir_name: str,
                           tmp_dir: Generator[Path, None, None]) -> None:
    out_dir = tmp_dir
    mk_dir_path = out_dir / made_dir_name

    # shallow
    func_shallow = make_sample(out_dir=mk_dir_path,
                               display=False, mkdir='shallow')
    func_shallow(**param)
    shallow_paths = [mk_dir_path / 'a=relu,hls=100_200,vf=0.1' / filename
                     for filename in filenames]
    assert_eio(*shallow_paths)


def test_eio_mkdir_deep(param: dict[str, list[int] | str | float | int],
                        filenames: list[str],
                        made_dir_name: str,
                        tmp_dir: Generator[Path, None, None]) -> None:
    out_dir = tmp_dir
    paths = [out_dir / filename for filename in filenames]
    mk_dir_path = out_dir / made_dir_name

    # deep
    func_deep = make_sample(out_dir=mk_dir_path,
                            display=False, mkdir='deep')
    func_deep(**param)
    deep_out_json_path = mk_dir_path / 'a=relu' / 'hls=100_200' / 'vf=0.1' / 'sample,a=relu,hls=100_200,vf=0.1,_s=2525.json'
    deep_out_json_path = mk_dir_path / 'a=relu' / 'hls=100_200' / 'vf=0.1' / 'sample,a=relu,hls=100_200,vf=0.1,_s=2525.json'
    deep_out_csv_path = mk_dir_path / 'a=relu' / 'hls=100_200' / 'vf=0.1' / 'sample,a=relu,hls=100_200,vf=0.1,_s=2525.csv'
    deep_paths = [mk_dir_path / 'a=relu' / 'hls=100_200' / 'vf=0.1' / filename for filename in filenames ]
    assert_eio(*deep_paths)
