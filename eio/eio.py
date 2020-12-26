# -*- coding: utf-8 -*-
import pandas as pd
import time, json
from .support_numpy import support_numpy
from .convert_param_to_list import convert_param_to_list
from .ParamEncoder import ParamEncoder
from .make_param_str import make_param_str

def eio(out_dir='./', stop_watch=True, trace_back=False,
        display=True, error_display=False,
        header=None, param=True,
        sort_keys=True, ensure_ascii=False,
        mkdir='off',
        indent=4, default=support_numpy, tail_param=('_seed_index', '_seed')):
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

            # パラメータの順番を整えるためにリスト化。[key, value]を要素として持つ
            param_list = convert_param_to_list(kargs, tail_param=tail_param)

            param_encoder = ParamEncoder() # 後で出力ディレクトリのパスを作るためにも使う
            keys = [p[0] for p in param_list]
            param_encoder.fit(keys)
            filename_param_str = make_param_str(param_list, param_encoder=param_encoder, sep=',')
            # 出力ディレクトリの作成
            if mkdir == 'shallow':
                dirname_param_str = make_param_str(param_list[:-2], param_encoder=param_encoder, sep=',')
                output_dir = out_dir + '/' + dirname_param_str + '/'
            elif mkdir == 'deep':
                dirname_param_str = make_param_str(param_list[:-2], param_encoder=param_encoder, sep='/')
                output_dir = out_dir + '/' + dirname_param_str + '/'
            else: # mkdir == 'on' or mkdir == 'off'
                output_dir = out_dir + '/'

            if mkdir == 'on' or mkdir == 'shallow' or mkdir == 'deep':
                os.makedirs(output_dir, exist_ok=True)

            def json_write(result):
                result_json_str = json.dumps(result, sort_keys=sort_keys,
                                             ensure_ascii=ensure_ascii, indent=indent,
                                             default=default)
                with open('{}/{},{}.json'.format(output_dir, l_header, filename_param_str), 'w', encoding='utf-8') as f:
                    f.write(result_json_str)

            if isinstance(result, dict):
                if param:
                    result['_param'] = kargs
                if stop_watch:
                    result['_process_time'] = process_time
                if error_display and 'error_type' in result: #エラーが起きたとき
                    print(result)
                json_write(result)
            elif hasattr(result, '__iter__'):
                dict_cnt, df_cnt = 0, 0
                for res in result:
                    if isinstance(res, dict):
                        if param:
                            res['_param'] = kargs
                        if stop_watch:
                            res['_process_time'] = process_time
                        json_write(res)
                        if error_display and 'error_type' in res: #エラーが起きたとき
                            print(res)
                    if isinstance(res, pd.DataFrame):
                        tail = '' if df_cnt == 0 else ('_' + str(df_cnt))
                        res.to_csv('{}/{},{}{}.csv'.format(output_dir, l_header, filename_param_str, tail))
                        df_cnt += 1
            if display:
                print('[{}m] finished: {}'.format(round(process_time / 60.0, 2), filename_param_str))
            return result
        return _decorated_func
    return _eio
