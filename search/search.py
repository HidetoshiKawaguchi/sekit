# -*- coding: utf-8 -*-
import os.path as op
import pandas as pd
import json

def search(filepath_list, out_funcs=tuple(), types=(str, int, float),
           header_key='_header', param_key='_param', filename_key='_filename',
           target_df=None, display=False):
    if target_df is None: # 追加先のdf
        target_df = pd.DataFrame()
        cached_filepath_set = set()
    else:
        cached_filepath_set = set(target_df[filename_key])

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
        params = params | set(k for k in result[param_key].keys())
        row_dict = {k:v for k, v in result.items() if type(v) in types and k != param_key}
        row_dict.update(result[param_key])
        row_dict[filename_key] = op.basename(filepath)
        for k, func in out_funcs:
            row_dict[k] = func(result)
        target_df = target_df.append(row_dict, ignore_index=True)
        if display:
            print('added ' + filepath)

    all_columns = set(target_df.columns)
    head_columns = {header_key, }
    tail_columns = {'_process_time', '_filename'}
    out_columns = all_columns - params - head_columns - tail_columns
    return pd.concat([target_df[sorted(head_columns)],
                      target_df[sorted(params)],
                      target_df[sorted(out_columns)],
                      target_df[sorted(tail_columns)]], axis=1)

if __name__ == '__main__':
    pass
