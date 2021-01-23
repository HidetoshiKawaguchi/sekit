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

class TestUtils(unittest.TestCase):
    def setUp(self):
        self.param = {
            'hidden_layer_sizes': [100, 200],
            'activation':'relu',
            'validation_fraction':0.1,
            '_seed': 2525
        }

    def test_convert_papram_to_list(self):
        p_list = convert_param_to_list(self.param)
        self.assertEqual(p_list[0][0], 'activation')
        self.assertEqual(p_list[0][1], 'relu')
        self.assertEqual(p_list[1][0], 'hidden_layer_sizes')
        self.assertEqual(p_list[1][1][0], 100)
        self.assertEqual(p_list[1][1][1], 200)
        self.assertEqual(p_list[2][0], 'validation_fraction')
        self.assertEqual(p_list[2][1], 0.1)

    def test_ParamEncoder(self):
        pe = ParamEncoder()
        param_train = [
            'activation',
            'hidden_layer_sizes',
            'validation_fraction',
            'vaaaaaaaaaa_fraaaaaaaaaaaaaa',
            'vbbbaaaaaaaaa_frbbbaaaaaaaaaaaaaa',
        ]
        transformed_1 = pe.fit_transform(param_train)
        self.assertEqual(transformed_1[0], 'a')
        self.assertEqual(transformed_1[1], 'hls')
        self.assertEqual(transformed_1[2], 'vf')
        self.assertEqual(transformed_1[3], 'vf1')
        self.assertEqual(transformed_1[4], 'vf2')

        param_2 = [
            'hidden_layer_sizes',
            'activation',
            'validation_fraction'
        ]
        transformed_2 = pe.transform(param_2)
        self.assertEqual(transformed_2[0], 'hls')
        self.assertEqual(transformed_2[1], 'a')
        self.assertEqual(transformed_2[2], 'vf')


    def test_transform_param_value(self):
        self.assertEqual(transform_param_value('aaa'), 'aaa')
        self.assertEqual(transform_param_value(1), "1")
        self.assertEqual(transform_param_value(None), 'null')
        self.assertEqual(transform_param_value(None, none_str='None'), 'None')
        self.assertEqual(transform_param_value([100, 200]), '100_200')
        self.assertEqual(transform_param_value([100, 200], sep='-'), '100-200')
        self.assertEqual(transform_param_value((100, 200)), '100_200')
        self.assertEqual(transform_param_value((100, 200), sep='-'), '100-200')
        self.assertEqual(transform_param_value({'a':0.1, 'b':'hoge'}), 'a-0.1_b-hoge')
        self.assertEqual(transform_param_value({'a':0.1, 'b':'hoge'}, sep=',',  kv=':'), 'a:0.1,b:hoge')


    def test_make_param_str(self):
        param_str = make_param_str(self.param)
        self.assertEqual(param_str, '_s=2525,a=relu,hls=100_200,vf=0.1')

        pe = ParamEncoder()
        pe.fit(self.param)
        param_str = make_param_str(self.param, param_encoder=pe)
        self.assertEqual(param_str, '_s=2525,a=relu,hls=100_200,vf=0.1')

        param_str = make_param_str(self.param, connector=':', sep='|')
        self.assertEqual(param_str, '_s:2525|a:relu|hls:100_200|vf:0.1')

if __name__ == '__main__':
    unittest.main()
