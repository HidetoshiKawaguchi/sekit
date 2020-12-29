# -*- coding:utf-8 -*-
from itertools import product
import pandas as pd
import numpy as np
import random

def _get_param_out(in_df, sep, ignore):
    param = []
    outkey = []
    param_flag = True
    for c in in_df.columns:
        if c == sep:
            param_flag = False
            continue
        if not c in ignore:
            if param_flag:
                param.append(c)
            elif param_flag is False and in_df[c].dtype == np.float64:
                outkey.append(c)
    return param, outkey

def _compile(in_df, param, outkey, connector='_________'):
    stats_dict = dict()
    for _, row in in_df.iterrows():
        param_hash = connector.join(str(row[p]) for p in param)
        if param_hash not in stats_dict.keys():
            stats_dict[param_hash] = {k:[] for k in outkey}
        for k in outkey:
            stats_dict[param_hash][k].append(row[k])
    return stats_dict

def stats(in_df, sep='|', ignore=('_seed', '_filename'), count_key='_n',
          stat_funcs=(('(ave)', np.average), ('(std)', np.std), ('(min)', np.min), ('(max)', np.max)),
          n_samples=None):
    # パラメータと出力の取得
    param, outkey = _get_param_out(in_df, sep, ignore)
    dtypes = {k:v for k, v in in_df.dtypes.items() if k in param}
    ## dtypesは最後に出力のdfの型を保持するために必要

    # dictに集計
    connector = '_________' # 本当はなくてもいいような処理にしたいが、時間がかかるので今はおいておく
    stats_dict = _compile(in_df, param, outkey, connector=connector)

    # dfに集計
    stat_outkey = ['{}{}'.format(o, sf[0]) for o, sf in product(outkey, stat_funcs)]
    result_df = pd.DataFrame(columns=param + [count_key, sep] + stat_outkey)
    for key, sampling_values in stats_dict.items():
        param_values = key.split(connector)
        row = {k:pv for k, pv in zip(param, param_values)}
        for out_k, sv in sampling_values.items():
            ss = len(sv) if n_samples is None else min(n_samples, len(sv))
            sv = random.sample(sv, ss)
            for s, f in stat_funcs:
                row[out_k + s] = f(sv)
            row[count_key] = ss
        result_df = result_df.append(row, ignore_index=True)

    result_df[sep] = sep
    result_df = result_df.astype(dtypes)
    return result_df
