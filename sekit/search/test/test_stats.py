# -*- coding: utf-8 -*-
import os, sys, unittest, json, glob
import os.path as op
_base = op.join(op.dirname(op.abspath(__file__)), '..', '..')
sys.path.append(_base)

import numpy as np
import pandas as pd
from search.lib import search
from search.lib import stats

class TestSearch(unittest.TestCase):
    def test_smoke(self):
        pattern = op.join(_base, 'search', 'test', 'result', '*.json')
        filepath_list = tuple(filepath for filepath in glob.glob(pattern))
        df = search(filepath_list,
                    out_funcs=(('hoge+piyo', lambda r: r['hoge'] + r['piyo']), ))
        stats_df = stats(df)
        stats_df.to_csv(op.join(_base, 'search', 'test', 'sample_stats.csv'))

        self.assertEqual(len(stats_df), 14)
        self.assertEqual(len(stats_df.columns), 22)
        self.assertEqual(stats_df['_n'][0], 3)

        check_df = stats_df[stats_df['activation'] == 'relu']
        check_df = check_df[check_df['hidden_layer_sizes'] == '[100, 200]']
        check_df = check_df[check_df['validation_fraction'] == 0.1]
        check_df = check_df.reset_index()
        self.assertAlmostEqual(check_df['hoge(ave)'][0], 600.781296680204)
        self.assertAlmostEqual(check_df['hoge(std)'][0], 0.537226908738035)
        self.assertAlmostEqual(check_df['hoge(min)'][0], 600.206247323861)
        self.assertAlmostEqual(check_df['hoge(max)'][0], 601.498830434484)

        # n_samplesを確かめる。
        stats_df = stats(df, n_samples=2)
        self.assertEqual(stats_df['_n'][0], 2)
        stats_df = stats(df, n_samples=1000000)
        self.assertEqual(stats_df['_n'][0], 3)


    def test_sampling(self):
        filepath = op.join(op.dirname(op.abspath(__file__)), 'test_sample_for_sampling.csv')
        raw_df = pd.read_csv(filepath, index_col=0)
        for _ in range(10):
            df = stats(raw_df, ignore=('_seed', ), n_samples=3,
                       stat_funcs=(('(ave)', lambda v: round(np.average(v), 4)),))
            flag = all((df['hoge(ave)'] == df['goro(ave)']) & \
                       (df['goro(ave)'] == df['piyo(ave)']))
            self.assertTrue(flag)


if __name__ == '__main__':
    unittest.main()
