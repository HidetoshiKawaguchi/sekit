# -*- coding: utf-8 -*-
import os, sys, unittest, json, glob
import os.path as op
_base = op.join(op.dirname(op.abspath(__file__)), '..', '..')
sys.path.append(_base)

import pandas as pd
from search.lib import search

class TestSearch(unittest.TestCase):
    def test_smoke(self):
        pattern = op.join(_base, 'search', 'test', 'result', '*.json')
        filepath_list = tuple(filepath for filepath in glob.glob(pattern))
        df = search(filepath_list,
                    out_funcs=(('hoge+piyo', lambda r: r['hoge'] + r['piyo']), ))
        df_filepath = op.join(_base, 'search', 'test', 'sample_search.csv')
        df.to_csv(df_filepath)
        cached_df = pd.read_csv(df_filepath)[:10]
        cached_df = search(filepath_list, target_df=cached_df)

        self.assertEqual(len(cached_df), 42)

if __name__ == '__main__':
    unittest.main()
