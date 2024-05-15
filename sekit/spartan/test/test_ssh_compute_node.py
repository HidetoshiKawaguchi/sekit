# -*- coding: utf-8 -*-
import unittest
import os
import sys
import time
from queue import Queue
from subprocess import getoutput

# リポジトリの一番上の階層.
# どこでも使うので、関数の外で定義
base = os.path.dirname(os.path.abspath(__file__)) + '/../'

sys.path.append(base)
from lib import SshComputeNode

class TestSshComputeNode(unittest.TestCase):
    def test_ssh_compute_node(self):
        ### テストに必要な情報
        ssh_n_cpu = 16
        ssh_hostname = 'cassia'
        commands = ['hostname', 'ls'] #何でも良い

        #### ローカルホスト
        cn = SshComputeNode(ssh_hostname)
        self.assertEqual(1, cn.n_jobs)
        cn = SshComputeNode(ssh_hostname, n_jobs=4)
        self.assertEqual(4, cn.n_jobs)
        cn = SshComputeNode(ssh_hostname, n_jobs=-1)
        self.assertEqual(ssh_n_cpu, cn.n_jobs)

        cn = SshComputeNode(ssh_hostname, n_jobs=8,
                            device=['cuda:0', 'cuda:1'])
        self.assertEqual(0, cn.device_state['cuda:0'])
        self.assertEqual(0, cn.device_state['cuda:1'])

        cn = SshComputeNode(ssh_hostname, n_jobs=2)
        filepath_list = [
            './___TestExperiment_Manager_{}.txt'.format(i)
            for i in range(5)
        ]
        commands = ['sleep 1; touch {};'.format(fp) for fp in filepath_list]
        q_commands = Queue()
        for c in commands:
            q_commands.put(c)
        cn.start(q_commands)
        cn.wait_all()
        cmd = 'ssh ' + ssh_hostname + ' ls -l ./___TestExperiment_Manager* | wc -l'
        stdout = int(getoutput(cmd))
        self.assertEqual(5, stdout)
        for fp in filepath_list:
            getoutput('ssh {} rm {}'.format(ssh_hostname, fp))



if __name__ == '__main__':
    unittest.main()
