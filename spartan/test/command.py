# -*- coding: utf-8 -*-
import os, sys, json


if __name__ == '__main__':
    input_dict = json.loads(sys.argv[1])
    filename = 'TestSpartan,a={},b={},_seed={}.json'.format(input_dict['a'], input_dict['b'],
                                           input_dict['_seed'])
    out_filepath = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        filename)
    with open(out_filepath, 'w') as f:
        json.dump(input_dict, f)
