# -*- coding: utf-8 -*-
import os
import os.path as op
import pandas as pd
import time, json
from .support_numpy import support_numpy
from .convert_param_to_list import convert_param_to_list
from .ParamEncoder import ParamEncoder
from .make_param_str import make_param_str


def _make_output_dir(mkdir, out_dir, param_list, param_encoder, tail_param):
    if mkdir == 'shallow':
        dirname_param_str = make_param_str(param_list[:-len(tail_param)],
                                           param_encoder=param_encoder,
                                           sep=',')
        output_dir = op.join(out_dir, dirname_param_str)
    elif mkdir == 'deep':
        dirname_param_str = make_param_str(param_list[:-len(tail_param)],
                                           param_encoder=param_encoder,
                                           sep='/')
        output_dir = op.join(out_dir, dirname_param_str)
    else: # mkdir == 'on' or mkdir == 'off'
        output_dir = out_dir
    return output_dir

def _make_output_info(out_dir, kargs, tail_param, mkdir):
    # パラメータの順番を整えるためにリスト化。[key, value]を要素として持つ
    param_list = convert_param_to_list(kargs, tail_param=tail_param)
    param_encoder = ParamEncoder() # 後で出力ディレクトリのパスを作るためにも使う
    param_encoder.fit([p[0] for p in param_list])
    filename_param_str = make_param_str(param_list, param_encoder=param_encoder, sep=',')
    output_dir = _make_output_dir(mkdir, out_dir, param_list,
                                  param_encoder, tail_param)
    return output_dir, filename_param_str

def eio(out_dir='./', header=None, param=True,
        process_time=True, trace_back=False,
        display=True, error_display=False,
        sort_keys=True, ensure_ascii=False,
        mkdir='off',
        indent=4, default=support_numpy, tail_param=('_seed', )):
    def _eio(func):
        def _decorated_func(*args, **kargs):
            l_header = func.__name__ if header is None else header
            start_time = time.time()
            if(trace_back):
                result = func(*args, **kargs)
            else:
                try:
                    result = func(*args, **kargs)
                except Exception as e:
                    result = {
                        'error_type': str(type(e)),
                        'error_args': str(e.args),
                        'error_self': str(e)
                    }
            process_time = time.time() - start_time

            # 出力ディレクトリとファイル名の文字列の作成
            ## out_dir: 出力先のディレクトリ
            ## kargs: 実験用関数のパラメータ(dict)
            ## tail_param: 文字列生成時に末尾に持ってくるパラメータ
            ## mkdir: ディレクトリの作成モード
            output_dir, filename_param_str = _make_output_info(out_dir, kargs, tail_param, mkdir)
            if mkdir == 'on' or mkdir == 'shallow' or mkdir == 'deep':
                os.makedirs(output_dir, exist_ok=True)

            # 出力ディレクトリとファイル名の文字列を使って、実際に書き込む
            ## JSON用の書き込みメソッド
            def write_json(result, cnt=0):
                if param:
                    result['_param'] = kargs
                if process_time:
                    result['_process_time'] = process_time
                if error_display and 'error_type' in result: #エラーが起きたとき
                    print(result)
                result_json_str = json.dumps(result, sort_keys=sort_keys,
                                             ensure_ascii=ensure_ascii, indent=indent,
                                             default=default)
                tail = '' if cnt == 0 else ('_' + str(cnt))
                filename = '{},{}{}.json'.format(l_header, filename_param_str, tail)
                outpath = op.join(output_dir, filename)
                with open(outpath, 'w', encoding='utf-8') as f:
                    f.write(result_json_str)

            ## CSV用の書き込みメソッド
            def write_csv(df, cnt=0):
                tail = '' if cnt == 0 else ('_' + str(cnt))
                filename = '{},{}{}.csv'.format(l_header, filename_param_str, tail)
                outpath = op.join(output_dir, filename)
                df.to_csv(outpath)

            if isinstance(result, dict):
                write_json(result)
            elif isinstance(result, pd.DataFrame):
                write_csv(result)
            elif hasattr(result, '__iter__'):
                dict_cnt, df_cnt = 0, 0
                for res in result:
                    if isinstance(res, dict):
                        write_json(res, dict_cnt)
                        dict_cnt += 1
                    if isinstance(res, pd.DataFrame):
                        write_csv(res, df_cnt)
                        df_cnt += 1
            if display:
                minute = round(process_time / 60.0, 2)
                print('[{}m] finished: {}'.format(minute, filename_param_str))
            return result
        return _decorated_func
    return _eio







