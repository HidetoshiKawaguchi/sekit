# -*- coding: utf-8 -*-
import pytest
import numpy as np
import pandas as pd

from sekit.utils import convert_param_to_list
from sekit.utils import ParamEncoder
from sekit.utils import transform_param_value
from sekit.utils import make_param_str
from sekit.utils import support_numpy


@pytest.fixture
def param():
    return {
        'hidden_layer_sizes': [100, 200],
        'activation':'relu',
        'validation_fraction':0.1,
        '_seed': 2525,
    }


def test_convert_papram_to_list(param):
    p_list = convert_param_to_list(param)
    assert p_list[0][0] == 'activation'
    assert p_list[0][1] == 'relu'
    assert p_list[1][0] == 'hidden_layer_sizes'
    assert p_list[1][1][0] == 100
    assert p_list[1][1][1] == 200
    assert p_list[2][0] ==  'validation_fraction'
    assert p_list[2][1] ==  0.1


@pytest.mark.parametrize("test_input,expected", [
    (
        [
            'activation',
            'hidden_layer_sizes',
            'validation_fraction',
            'vaaaaaaaaaa_fraaaaaaaaaaaaaa',
            'vbbbaaaaaaaaa_frbbbaaaaaaaaaaaaaa',
        ],
        [
            'a', 'hls', 'vf', 'vf1', 'vf2'
        ]
    ),
    (
        [
            'hidden_layer_sizes',
            'activation',
            'validation_fraction'
        ],
        [
            'hls',
            'a',
            'vf'
        ]
    )    
])
def test_ParamEncoder(test_input, expected):
    pe = ParamEncoder()
    transformed = pe.fit_transform(test_input)
    assert transformed == expected


def test_transform_param_value():
    assert transform_param_value('aaa') ==  'aaa'
    assert transform_param_value(1) ==  "1"
    assert transform_param_value(None) ==  'null'
    assert transform_param_value(None, none_str='None') == 'None'
    assert transform_param_value([100, 200]) == '100_200'
    assert transform_param_value([100, 200], sep='-') ==  '100-200'
    assert transform_param_value((100, 200)) ==  '100_200'
    assert transform_param_value((100, 200), sep='-') == '100-200'
    assert transform_param_value({'a':0.1, 'b':'hoge'}) ==  'a-0.1_b-hoge'
    assert transform_param_value({'a':0.1, 'b':'hoge'}, sep=',',  kv=':') == 'a:0.1,b:hoge'


def test_make_param_str(param):
    param_str = make_param_str(param)
    assert param_str == '_s=2525,a=relu,hls=100_200,vf=0.1'

    pe = ParamEncoder()
    pe.fit(param)
    param_str = make_param_str(param, param_encoder=pe)
    assert param_str == '_s=2525,a=relu,hls=100_200,vf=0.1'

    param_str = make_param_str(param, connector=':', sep='|')
    assert param_str == '_s:2525|a:relu|hls:100_200|vf:0.1'


@pytest.mark.parametrize('test_input,expected_value,expected_type',
                         [
                             (np.float32(3.14), pytest.approx(3.14), float),
                             (np.int64(100), 100, int),
                             (np.array([1, 2, 3]), [1, 2, 3], list)
                         ])
def test_support_numpy(test_input, expected_value, expected_type):
    actual = support_numpy(test_input)
    assert actual == expected_value
    assert type(actual) == expected_type

