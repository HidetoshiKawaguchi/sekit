# coding:utf-8
import os
import json
import scipy
import numpy as np
import scipy.spatial.distance as distance
import itertools
from scipy.cluster.hierarchy import linkage, dendrogram
from random import random, sample
import pandas as pd
import traceback
import time
import pandas as pd
import glob
from itertools import product


# CSVファイルのラベル毎にデータIDのリストを保持したDictを返す関数
def make_label_Id_list(array_of_2d, label_id = -1):
    result = {}
    for i, row in enumerate(array_of_2d):
        label = row[label_id]
        if label not in result:
            result[label] = []
        result[label].append(i)
    return result

# ラベルのリストを0からスタートの整数に置き換える関数
# 返り値はList型になる.
def conv_labels_zero_to_n(labels):
    # ラベルを順序を保持しながらユニークにする.
    # 順序を保持するためにsetを介すやりかたは使わない。
    # 内包表記を使うともっと早くなるらしいがわかりやすさのためにfor文を使う。
    labels_uniq = []
    for label in labels:
        if label not in labels_uniq:
            labels_uniq.append(label)
    return list(map(lambda obj: labels_uniq.index(obj), labels))


# make_label_Id_list関数で得たDictから、ラベル毎（Key毎）に指定した数のIDのリストを返す関数
def pickup_random_Id_list(dict, num_pick = 2):
    result = {}
    for label, id_list in dict.items():
        result[label] = sample(id_list, num_pick)
    return result

def make_must_link_list(dict):
    result = []
    for id_list in dict.values():
        result.extend(itertools.combinations(id_list, 2))
    return result

def make_cannot_link_list(dict):
    result = []
    values_list = list(dict.values())
    for i in range(len(values_list) - 1):
        for j in range(i + 1, len(values_list)):
            result.extend(list(itertools.product(values_list[i], values_list[j])))
    return result

# json.dumpsでdictをjson文字列へ変換するときに、numpyの型へ対応するためのメソッド
## (例)json.dumps(result, sort_keys = True, indent = 4, default=support_numpy )
def support_numpy(o):
    if isinstance(o, np.float32):
        return float(o)
    if isinstance(o, np.int64):
        return int(o)
    if isinstance(o, np.ndarray):
        return list(o)
    raise TypeError(repr(o) + " is not JSON serializable")

## numpy配列はpopを使えないため以下のflattenは実装しないものとする。速いのは速いらしい
# def flatten(l):
#     import collections
#     i = 0
#     while i < len(l):
#         while isinstance(l[i], collections.Iterable):
#             if not l[i]:
#                 l.pop(i)
#                 i -= 1
#                 break
#             else:
#                 l[i:i + 1] = l[i]
#         i += 1
#     return l


def flatten(l):
    import collections
    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, str):
            for sub in flatten(el):
                yield sub
        else:
            yield el

def check(x, y):
    return [xy[0] == xy[1] for xy in zip(x, y)]


class ParamEncoder:
    """実験用パラメータを短縮文字に変換するためのクラス
    """
    def __init__(self, sep='_'):
        self.mapping_ = {}
        self.sep = sep
        pass

    def encode(self, param, sep=None):
        """ 与えられたパラメータをある規則に従って短縮形で返すメソッド. 内部状態にも依存する。
        '_'で単語を区切る.

        Parameters
        ----------
        param: String
            name of parameter
        Returns
        -------
        String
        """
        if sep is None:
            sep = self.sep

        if param in self.mapping_: # ある場合はそのまま返す
            return self.mapping_[param]

        import re
        head = sep if re.match(r'{}'.format(sep), param) else ''
        short_param = head + ''.join(w[0] for w in param.split(sep) if w != '')

        if short_param in self.mapping_.values(): #すでに同じ短縮版のパラメータがある場合
            cnt = 0
            for o in self.mapping_.values():
                if re.match(r'{}'.format(short_param), o):
                   cnt += 1
            short_param += str(cnt)

        self.mapping_[param] = short_param

        return short_param


    def fit(self, params):
        """パラメータのリストをインプットとして、短縮形を生成し保持する。

        Parameters
        ----------
        params: 1d array-like
            names of parameters for a experiment.
        Returns
        -------
        self
        """
        for p in params:
            self.encode(p, sep=self.sep)
        return self


    def transform(self, params):
        """パラメータのリストを単語ごとにショート版に変換して返す

        Parameters
        ----------
        params: 1d array-like
            names of parameters for a experiment.
        Returns
        -------
        list
        """
        return [self.mapping_[p] for p in params]

    def fit_transform(self, params):
        return self.fit(params).transform(params)

    def inverse_transform(self, s_params):
        inverse_mapping = {v: k for k, v in self.mapping_.items()}
        return [inverse_mapping[sp] for sp in s_params]


def transform_para_value(obj, sep='_', none_str='null',
                         kv='-', dict_reverse=False):
    """ 実験の値を文字列に変換する関数. 主にファイル名の生成のために使う

    Parameters
    ---------
    obj: object
        transformed value
    Return
    ------
    String
    """
    if obj is None:
        return none_str
    elif isinstance(obj, list):
        return sep.join(str(o) for o in obj)
    elif isinstance(obj, dict):
        linked_dict = list([str(a), str(b)] for a, b in obj.items())
        # 順番が変わると困るので、同じ値になるためにキーでソートしておく
        sorted_linked_dict = sorted(linked_dict, key=lambda d: str(d[0]),
                                    reverse=dict_reverse)
        return sep.join(k + kv + v for k, v in sorted_linked_dict)
    else:
        return str(obj)


def make_param_str(params, param_encoder=None, connector='=', sep=','):
    """パラメータ名と値がセットになっているdictかそれをリストに変換したものを入力として、１つの文字列を生成する関数
    Parameters
    ----------
    params: dict or 2d array-like
        入力となるパラメータ郡.dictの場合はパラメータを勝手にソーティングする。2d array-likeの場合はその順番で行う.
    param_encoder: an instance of ParamEncoder
        短縮文字列を使うParamEncoderオブジェクト. 指定しなければ内部でインスタンスを生成してそれを使う
    """
    if isinstance(params, dict):
        params = sorted(list(params.items()), key=lambda kv: str(kv[0]))

    if param_encoder is None:
        param_encoder = ParamEncoder()

    def make_element(k, v):
        return connector.join([param_encoder.encode(k), transform_para_value(v)])
    file_str = sep.join(make_element(k, v) for k, v in params)

    return file_str

def convert_param_to_list(param, tail_params=('_seed_index', '_seed')):
    """パラメータのdictを並びかえて, リスト形式にするジェネレータ関数.
    Parameters
    ----------
    param: dict
        keyがパラメータ名, valueがそのパラメータの値を示すdict型の関数
    tail_params: array-like
        返り値のおしりに持ってきたいパラメータのリスト
    Return
    ------
    2d array-like
    """
    param_list = sorted(list(param.items()), key=lambda kv: str(kv[0]))
    head_params_list = [kv for kv in param_list if kv[0] not in tail_params]
    tail_params_list = [[para, param.get(para)] for para in tail_params if param.get(para) is not None]

    return head_params_list + tail_params_list


def experiment(out_base='./', stop_watch=True, trace_back=False,
               display=False, error_display=False,
               header=None, params=True,
               sort_keys=True, ensure_ascii=False,
               mkdir='off',
               indent=4, default=support_numpy, tail_params=('_seed_index', '_seed')):
    def _experiment(func):
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
            param_list = convert_param_to_list(kargs, tail_params=tail_params)

            param_encoder = ParamEncoder() # 後で出力ディレクトリのパスを作るためにも使う
            keys = [p[0] for p in param_list]
            param_encoder.fit(keys)
            filename_param_str = make_param_str(param_list, param_encoder=param_encoder, sep=',')
            # 出力ディレクトリの作成
            if mkdir == 'shallow':
                dirname_param_str = make_param_str(param_list[:-2], param_encoder=param_encoder, sep=',')
                output_dir = out_base + '/' + dirname_param_str + '/'
            elif mkdir == 'deep':
                dirname_param_str = make_param_str(param_list[:-2], param_encoder=param_encoder, sep='/')
                output_dir = out_base + '/' + dirname_param_str + '/'
            else: # mkdir == 'on' or mkdir == 'off'
                output_dir = out_base + '/'

            if mkdir == 'on' or mkdir == 'shallow' or mkdir == 'deep':
                os.makedirs(output_dir, exist_ok=True)

            def json_write(result):
                result_json_str = json.dumps(result, sort_keys=sort_keys,
                                             ensure_ascii=ensure_ascii, indent=indent,
                                             default=default)
                with open('{}/{},{}.json'.format(output_dir, l_header, filename_param_str), 'w', encoding='utf-8') as f:
                    f.write(result_json_str)

            if isinstance(result, dict):
                if params:
                    result['params'] = kargs
                if stop_watch:
                    result['process_time'] = process_time
                if error_display and 'error_type' in result: #エラーが起きたとき
                    print(result)
                json_write(result)
            elif hasattr(result, '__iter__'):
                dict_cnt, df_cnt = 0, 0
                for res in result:
                    if isinstance(res, dict):
                        if params:
                            res['params'] = kargs
                        if stop_watch:
                            res['process_time'] = process_time
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
    return _experiment

def gen_param(source): # パラメータを総当りする
    if type(source) is dict:
        source = source.items()
    keys = tuple(v[0] for v in source)
    values = (v[1] for v in source)
    for v in itertools.product(*values):
        yield {keys[index]:value for index, value in enumerate(v)}


def search(searched_dir, params_list, header, dir_type='root', out_funcs=tuple(), tail_params=('_seed_index', '_seed'),
           types=(str, int, float), display=False, mkdir='on', target_df=None):
    keys = sorted(params_list[0].keys()) # 基本的には1つ以上ある
    param_encoder = ParamEncoder()
    param_encoder.fit(keys)

    searched_glob_str = set()

    if target_df is None: # 追加先のdf
        target_df = pd.DataFrame(columns=keys)
        cached_filepath_set = set()
    else:
        cached_filepath_set = set(target_df['filepath'])

    for params in params_list:
        for param in gen_param(params.items()):
            for tail_param in tail_params:
                param[tail_param] = '*'
            param_list = convert_param_to_list(param, tail_params=tail_params)
            param_str = make_param_str(param_list, param_encoder=param_encoder, sep=',')
            if dir_type == 'shallow':
                dir_str = '/' + make_param_str(param_list[:-2], param_encoder=param_encoder, sep=',')
            elif dir_type == 'deep':
                dir_str = make_param_str(param_list[:-2], param_encoder=param_encoder, sep='/')
            else:
                dir_str = ''

            glob_str = searched_dir + '{}/{},{}.json'.format(dir_str, header, param_str)
            if glob_str in searched_glob_str:
                continue
            if(display):
                print(glob_str)

            for filepath in glob.glob(glob_str):
                if(filepath in cached_filepath_set):
                    if(display):
                        print('--- cached, ' + filepath)
                    continue

                if(display):
                    print('--- ' + filepath)

                with open(filepath, 'r') as f:
                    try:
                        result = json.load(f)
                        if 'error_type' in result:
                            continue
                    except:
                        continue
                standard_output_keys = [key for key in result if type(result[key]) in types]
                func_output_keys = [key for key, _ in out_funcs]
                output_keys = standard_output_keys + func_output_keys

                param_values = [result["params"][k] for k in keys]
                output_values = [result[key] for key in standard_output_keys] + [func(result) for _, func in out_funcs]
                s = pd.Series(param_values+output_values+[filepath], index=keys+output_keys+['filepath'])
                target_df = target_df.append(s, ignore_index=True)

            searched_glob_str.add(glob_str)

    # 最後にfilepath列を末尾に移動する。
    columns = target_df.columns.tolist()
    columns.remove('filepath')
    columns.append('filepath')
    target_df = target_df.ix[:, columns]
    return target_df


def statistics(in_df, param_keys, count_key='n',
               stat_funcs=(('(ave)', np.average), ('(std)', np.std), ('(min)', np.min), ('(max)', np.max)),
               n_samples=None):
    param_keys = list(param_keys)
    out_keys = tuple(k for k in in_df.columns if k not in tuple(param_keys))
    # param_tree = {key: set(in_df[key]) for key in param_keys}
    param_list = []

    pool = {}
    t_out_keys = None #あとで自動で入る
    for index, row in in_df.iterrows():
        param = {k: row[k] for k in param_keys}
        param_list.append(param)
        param_str = make_param_str(param)
        if param_str not in pool:
            if t_out_keys is None:
                t_out_keys = tuple(k for k in out_keys if type(row[k]) is int or type(row[k]) is float)
            pool[param_str] = {k:[] for k in t_out_keys}

        for k in t_out_keys:
            if row[k] is not None:
                if n_samples is None or len(pool[param_str][k]) < n_samples:
                    (pool[param_str][k]).append(row[k])

    # in_dfのうち、
    # (outputの値のkey, out_dfの統計値のためのkey, 統計量算出のための関数)
    # という構造になる
    out_info = list((o_key, o_key+s_func[0], s_func[1]) for o_key, s_func in product(t_out_keys, stat_funcs))
    columns = param_keys + [count_key] + [o[1] for o in out_info]
    out_df = pd.DataFrame(columns=columns)

    finished_param = [] # 終わったparamを管理するためのlist
    for param in param_list:
        param_str = make_param_str(param)
        if param_str in finished_param:
            continue

        # row変数をDataFrameの１行として値を追加していく
        ## 入力(実験パラメータ)の部分
        row = [param[key] for key in param_keys]

        ## サンプル数(outputの値によっては違う値が入っている可能性がある.t_out_keysの一要素毎にカウント
        n_dict = {k:len(v) for k, v in pool[param_str].items()}
        n_sampling_set = list(set(v for _, v in n_dict.items()))
        if len(n_sampling_set) == 1:
            n_info = n_sampling_set[0]
        else: # 1つでないときは、それぞれのカウント数をdict型でき術
            n_info = json.dumps(n_dict)
        row.append(n_info)

        ## 出力の部分. out_infoの情報に従って出力すれば良い
        for key, column_name, func in out_info:
            if pool[param_str].get(key, None) is not None:
                value = func(pool[param_str].get(key))
            else:
                value = None
            row.append(value)
        se = pd.Series(row, index=out_df.columns)
        out_df = out_df.append(se, ignore_index=True)

        finished_param.append(param_str)

    return out_df


class TexDataFrame(pd.DataFrame):
    def to_tex_table(self, indent=2, table_option='htb', tabuler_option=None, ndigits=3,
                     star=True, centering=True, caption=None, label=None, outline=['t', 'b', 'l', 'r'],
                     hline_list=[],
                     above_description=None,
                     bellow_description=None):
        def _make_column_pos():
            if type(tabuler_option) == str:
                return tabuler_option
            elif tabuler_option is None:
                out = ''
                if 'l' in outline:
                    out += '|'
                out = out + '|'.join('c' * len(self.columns))
                if 'r' in outline:
                    out += '|'
                return out
            else:
                raise ValueError('tabuler_optionにはstrかNoneをいれてください。')

        rows = []

        s = '*' if star else '' # ぶちぬきオプション
        # c = ' \centering' if centering else '' # 中央表示オプション

        # header
        rows.append("\\begin{{table{}}}[{}]".format(s, table_option))
        if centering is True:
            rows.append("{}\\begin{{center}}".format(' '*indent))
        if caption:
            rows.append('{}\\caption{{{}}}'.format('  '*indent, caption))
            if label:
                rows[-1] = rows[-1] + ' \\label{{{}}}'.format(label)
        if type(above_description) is str:
            rows.append(above_description)
        rows.append("{}\\begin{{tabular}}{{{}}}".format('  '*indent, _make_column_pos()))
        if 't' in outline:
            rows[-1] = rows[-1] + " \\hline"

        # columns
        rows.append('  '*indent + ' & '.join(self.columns) + ' \\\\ \\hline \\hline')

        # contents
        def _normalize(obj):
            if  type(obj) == str:
                return obj
            elif hasattr(obj, '__iter__'):
                return ','.join(obj)
            elif type(obj) == int:
                return str(obj)
            elif type(obj) == float or np.float64:
                return str(round(obj, ndigits))
            else:
                return obj

        for index, ro in self.iterrows():
            values = [_normalize(ro[c]) for c in self.columns]
            str_row = ('   '*indent) + ' & '.join(values) + ' \\\\'
            # line_listに入っている行番号に入っている数だけhlineを追加'
            for _ in [r for r in hline_list if r == index+1]:
                str_row = str_row + ' \\hline'
            rows.append(str_row)
        if 'b' in outline:
            rows[-1] = rows[-1] + ' \\hline'

        # tail
        rows.append("{}\\end{{tabular}}".format('  '*indent))
        if centering is True:
            rows.append('{}\\end{{center}}'.format(' '*indent))
        if type(bellow_description) is str:
            rows.append(' '*indent + bellow_description)
        rows.append("\\end{{table{}}}".format(s))
        return '\n'.join(rows)


if __name__ == '__main__':
    import numpy as np
    flatten_test_list = [1, 2, [3, 4, 5], [6, [7, [8, 9]]]]
    print(flatten_test_list)
    print(list(flatten(flatten_test_list)))
    x = [1, 2, 2, 4, 5]
    y = [1, 2, 3, 4, 5]
    print(check(x, y))
