# -*- coding: utf-8 -*-
import os.path as op
from itertools import chain
from glob import glob
import pandas as pd
import json

def search(filepath_list, dir=None,
           out_funcs=tuple(), types=(str, int, float),
           param_key='_param', filename_key='_filename', sep='|',
           head_columns=('_header',), tail_columns=('_process_time', '_filename'),
           target_df=None, display=False):
    if target_df is None: # 追加先のdf
        target_df = pd.DataFrame()
        cached_filepath_set = set()
    else:
        cached_filepath_set = set(target_df[filename_key])
    if dir is not None:
        filepath_list = chain(glob(op.join(dir, '*.json')), filepath_list)

    params = set()
    for filepath in filepath_list:
        if op.basename(filepath) in cached_filepath_set:
            if display:
                print('skip ' + filepath)
            continue
        with open(filepath, 'r') as f:
            try:
                result = json.load(f)
                if '_error_type' in result or not param_key in result:
                    continue
            except Exception as e:
                continue
        params = params | set(k for k in result.get(param_key, {}).keys())
        row_dict = {k:v for k, v in result.items() if type(v) in types and k != param_key}
        row_dict.update(result[param_key])
        row_dict[filename_key] = op.basename(filepath)
        for k, func in out_funcs:
            row_dict[k] = func(result)
        target_df = target_df.append(row_dict, ignore_index=True)
        if display:
            print('added ' + filepath)

    all_columns = set(target_df.columns)
    out_columns = all_columns - params - set(head_columns) - set(tail_columns) - set([sep])
    out_df = target_df[list(head_columns)]
    out_df = out_df.join(target_df[sorted(params)])
    if sep is not None and sep != '':
        out_df[sep] = sep
    out_df = out_df.join(target_df[sorted(out_columns)])
    out_df = out_df.join(target_df[list(tail_columns)])
    return out_df

if __name__ == '__main__':
    pass
