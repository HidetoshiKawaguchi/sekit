# -*- coding:utf-8 -*-
import random
from itertools import product

import numpy as np
import pandas as pd


def _get_param_out(in_df, sep, ignore):
    param = []
    outkey = []
    param_flag = True
    for c in in_df.columns:
        if c == sep:
            param_flag = False
            continue
        if c not in ignore:
            if param_flag:
                param.append(c)
            elif param_flag is False and (
                in_df[c].dtype == np.float64 or in_df[c].dtype == np.int64
            ):
                outkey.append(c)
    return param, outkey


def _sample(in_df, param, n_samples, connector="_________"):
    # パラメータの組み合わせ毎にindexを収集する
    sample_dict = dict()
    for index, row in in_df[param].iterrows():
        param_hash = connector.join(str(row[p]) for p in param)
        if param_hash not in sample_dict.keys():
            sample_dict[param_hash] = []
        sample_dict[param_hash].append(index)

    # パラメータの組み合わせ毎にindexをサンプリングする
    sampled_indices = set()
    for key, indices in sample_dict.items():
        ss = min(len(indices), n_samples)
        sampled_indices = sampled_indices | set(random.sample(indices, ss))
    return in_df[in_df.index.isin(sampled_indices)]


def _compile(in_df, param, outkey, connector="_________"):
    stats_dict = dict()
    for _, row in in_df.iterrows():
        param_hash = connector.join(str(row[p]) for p in param)
        if param_hash not in stats_dict.keys():
            stats_dict[param_hash] = {k: [] for k in outkey}
        for k in outkey:
            stats_dict[param_hash][k].append(row[k])
    return stats_dict


def stats(
    in_df,
    sep="|",
    ignore=("_seed", "_filename"),
    count_key="_n",
    stat_funcs=(
        ("(ave)", np.average),
        ("(std)", np.std),
        ("(min)", np.min),
        ("(max)", np.max),
    ),
    n_samples=None,
):
    connector = "_________"

    # パラメータと出力の取得
    param, outkey = _get_param_out(in_df, sep, ignore)
    dtypes = {
        k: v for k, v in in_df.dtypes.items() if k in param and v != bool
    }
    bool_params = {
        k for k, v in in_df.dtypes.items() if k in param and v == bool
    }
    # dtypesは最後に出力のdfの型を保持するために必要．ただし，bool型以外
    # bool_paramsは，bool型のパラメータ．最後まとめていると，bool型が全てTrueに変換されてしまうため，特別な処理が必要

    # n_samplesを基にサンプリング
    if n_samples is not None and n_samples > 0:
        in_df = _sample(in_df, param, n_samples, connector=connector)

    # dictに集計
    stats_dict = _compile(in_df, param, outkey, connector=connector)

    # dfに集計
    stat_outkey = [
        "{}{}".format(o, sf[0]) for o, sf in product(outkey, stat_funcs)
    ]
    row_list = []
    for key, sampling_values in stats_dict.items():
        param_values = key.split(connector)
        row = {k: pv for k, pv in zip(param, param_values)}
        for out_k, sv in sampling_values.items():
            for s, f in stat_funcs:
                row[out_k + s] = f(sv)
            row[count_key] = len(sv)
        row_list.append(row)
    result_df = pd.DataFrame(row_list)
    result_df[sep] = sep
    result_df = result_df.astype(dtypes)
    for bool_param in bool_params:
        # ここが曲者．astypeでまとめてboolに戻すと元がboolの列は全ての値がTrueになってしまう．
        result_df[bool_param] = result_df[bool_param].map(
            lambda p: p == "True"
        )
    return result_df
