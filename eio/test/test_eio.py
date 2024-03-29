# -*- coding: utf-8 -*-
import os
import unittest
import shutil
import os.path as op
_base = op.join(op.dirname(op.abspath(__file__)), '..', '..')
import sys, json
sys.path.append(_base)

import pandas as pd
from utils import convert_param_to_list
from utils import ParamEncoder
from utils import transform_param_value
from utils import make_param_str
from utils import support_numpy
from eio import eio

class TestEIO(unittest.TestCase):
    def setUp(self):
        self.param = {
            'hidden_layer_sizes': [100, 200],
            'activation':'relu',
            'validation_fraction':0.1,
            '_seed': 2525
        }
        self.filenames = [
            'sample,a=relu,hls=100_200,vf=0.1,_s=2525.json',
            'sample,a=relu,hls=100_200,vf=0.1,_s=2525.csv',
            'sample,a=relu,hls=100_200,vf=0.1,_s=2525_1.json',
            'sample,a=relu,hls=100_200,vf=0.1,_s=2525_1.csv',
            'sample,a=relu,hls=100_200,vf=0.1,_s=2525_2.csv'
        ]

    def assertJSON(self, result):
        self.assertEqual(result['a'][0], 200)
        self.assertEqual(result['a'][1], 400)
        self.assertEqual(result['b'], '___relu___')
        self.assertAlmostEqual(result['c'], 0.3)
        self.assertEqual(result['_param']['hidden_layer_sizes'][0], 100)
        self.assertEqual(result['_param']['hidden_layer_sizes'][1], 200)
        self.assertEqual(result['_param']['activation'], 'relu')
        self.assertEqual(result['_param']['validation_fraction'], 0.1)
        self.assertEqual(result['_param']['_seed'], 2525)

    def assertDf(self, df):
        self.assertEqual(df['a'][0], 100)
        self.assertEqual(df['b'][0], '___relu___')
        self.assertAlmostEqual(df['c'][0], 0.3)

    def assertEio(self, *args):
        for filepath in args:
            ext = os.path.splitext(filepath)[1]
            if ext == 'json':
                with open(file_path, 'r') as f:
                    so = json.load(f)
                    self.assertJSON(so)
            elif ext == 'csv':
                self.assertDf(pd.read_csv(file_path))

    def make_sample(self, out_dir='./', header=None, param_flag=True, header_flag=True,
                    process_time=True, trace_back=False,
                    display=True, error_display=False,
                    sort_keys=True, ensure_ascii=False,
                    mkdir='off',
                    indent=4, default=support_numpy, tail_param=('_seed', )):

        @eio(out_dir=out_dir, header=header, param_flag=param_flag, header_flag=header_flag,
             process_time=process_time, trace_back=trace_back,
             display=display, error_display=error_display,
             sort_keys=sort_keys, ensure_ascii=ensure_ascii,
             mkdir=mkdir,
             indent=indent, default=support_numpy, tail_param=tail_param)
        def sample(hidden_layer_sizes: tuple,
                   activation: str,
                   validation_fraction:float,
                   _seed:int) -> dict:
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


    def test_eio_smoke(self):
        out_dir = op.join(_base, 'eio', 'test')
        sample = self.make_sample(out_dir=out_dir, display=False)
        sample(**self.param)
        paths = [op.join(out_dir, fn) for fn in self.filenames]
        self.assertEio(*paths)

    def test_eio_mkdir(self):
        out_dir = op.join(_base, 'eio', 'test')
        mk_dir_path = op.join(out_dir, 'test_mkdir')
        try: #ディレクトリを一旦削除して作成されることを確かめる
            shutil.rmtree(mk_dir_path)
        except FileNotFoundError as e:
            pass

        # on
        func = self.make_sample(out_dir=mk_dir_path,
                                display=False, mkdir='on')
        paths = [op.join(mk_dir_path, fn) for fn in self.filenames]
        func(**self.param)
        self.assertEio(*paths)

        # shallow
        func_shallow = self.make_sample(out_dir=mk_dir_path,
                                        display=False, mkdir='shallow')
        func_shallow(**self.param)
        shallow_paths = [op.join(mk_dir_path, 'a=relu,hls=100_200,vf=0.1', fn)
                         for fn in self.filenames]
        self.assertEio(*shallow_paths)

        # deep
        func_deep = self.make_sample(out_dir=mk_dir_path,
                                     display=False, mkdir='deep')
        func_deep(**self.param)
        deep_out_json_path = op.join(mk_dir_path, 'a=relu', 'hls=100_200', 'vf=0.1',
                                     'sample,a=relu,hls=100_200,vf=0.1,_s=2525.json')
        deep_out_csv_path = op.join(mk_dir_path, 'a=relu', 'hls=100_200', 'vf=0.1',
                                    'sample,a=relu,hls=100_200,vf=0.1,_s=2525.csv')
        deep_paths = [op.join(mk_dir_path, 'a=relu', 'hls=100_200', 'vf=0.1', fn)
                      for fn in self.filenames ]
        self.assertEio(*deep_paths)


if __name__ == '__main__':
    unittest.main()
