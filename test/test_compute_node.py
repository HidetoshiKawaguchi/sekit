# -*- coding: utf-8 -*-
import unittest
import os
import sys
import time
from queue import Queue


# リポジトリの一番上の階層.
# どこでも使うので、関数の外で定義
base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.append(base)
from lib import ComputeNode

class TestComputeNode(unittest.TestCase):
    def test_compute_node(self):
        ### テストに必要な情報
        host_n_cpu = 72
        ssh_n_cpu = 16
        ssh_hostname = 'cassia'
        commands = ['hostname', 'ls'] #何でも良い

        #### ローカルホスト
        cn = ComputeNode()
        self.assertEqual(1, cn.n_jobs)
        cn = ComputeNode(n_jobs=4)
        self.assertEqual(4, cn.n_jobs)
        cn = ComputeNode(n_jobs=-1)
        self.assertEqual(host_n_cpu, cn.n_jobs)


        cn = ComputeNode(n_jobs=2)
        filepath_list = [
            os.path.join(base, 'test', '___TestExperiment_Manager_{}.txt'.format(i))
            for i in range(5)
        ]
        commands = ['sleep 1; touch {}'.format(fp) for fp in filepath_list]
        q_commands = Queue()
        for c in commands:
            q_commands.put(c)
        cn.start(q_commands)
        cn.wait_all()
        for filepath in filepath_list:
            self.assertTrue(os.path.exists(filepath))
            os.remove(filepath)


if __name__ == '__main__':
    unittest.main()
