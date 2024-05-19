# -*- coding: utf-8 -*-
import pytest
import os
import glob
from typing import Callable

from pathlib import Path
import pandas as pd

from sekit.search import search


def test_search(search_filepath_list: list[str],
                out_func_hoge_piyo: tuple[str, Callable[dict, int]]) -> None:
    df = search(search_filepath_list, out_funcs=(out_func_hoge_piyo, ))
    assert len(df) == 42
    assert list(df.columns) == [
        "_header",
        "_seed",
        "activation",
        "hidden_layer_sizes",
        "validation_fraction",
        "|",
        "goro",
        "hoge",
        "hoge+piyo",
        "piyo",
        "_process_time",
        "_filename"
    ]

    # キャッシュが機能しているかのテスト
    cached_df = df[:10]
    df2 = search(search_filepath_list, out_funcs=(out_func_hoge_piyo, ),
                 target_df=cached_df)
    assert len(df) == len(df2)
