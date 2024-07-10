from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
import pytest

from sekit.search import search
from sekit.stats import stats


def test_stats(
    search_filepath_list: list[str],
    out_func_hoge_piyo: tuple[str, Callable[dict[str, int], int]],
) -> None:
    df = search(search_filepath_list, out_funcs=(out_func_hoge_piyo,))
    stats_df = stats(df)

    assert len(stats_df) == 14
    assert len(stats_df.columns) == 22
    assert stats_df["_n"][0] == 3

    check_df = stats_df[stats_df["activation"] == "relu"]
    check_df = check_df[check_df["hidden_layer_sizes"] == "[100, 200]"]
    check_df = check_df[check_df["validation_fraction"] == 0.1]
    check_df = check_df.reset_index()
    assert check_df["hoge(ave)"][0] == pytest.approx(600.781296680204)
    assert check_df["hoge(std)"][0] == pytest.approx(0.537226908738035)
    assert check_df["hoge(min)"][0] == pytest.approx(600.206247323861)
    assert check_df["hoge(max)"][0] == pytest.approx(601.498830434484)

    # n_samplesを確かめる。
    stats_df = stats(df, n_samples=2)
    assert stats_df["_n"][0] == 2
    stats_df = stats(df, n_samples=1000000)
    assert stats_df["_n"][0] == 3


def test_sampling() -> None:
    filepath = Path(__file__).parent / "data" / "test_sample_for_sampling.csv"
    raw_df = pd.read_csv(filepath, index_col=0)
    for _ in range(10):
        df = stats(
            raw_df,
            ignore=("_seed",),
            n_samples=3,
            stat_funcs=(("(ave)", lambda v: round(np.average(v), 4)),),
        )
        assert all(
            (df["hoge(ave)"] == df["goro(ave)"])
            & (df["goro(ave)"] == df["piyo(ave)"])
        )
