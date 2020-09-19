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
from lib import Cluster
from lib import ComputeNode
from lib import SshComputeNode

class TestCluster(unittest.TestCase):
    def test_ssh_compute_node(self):
        #### ローカルホストだけ. デフォルト
        clstr = Cluster()
        self.assertEqual(ComputeNode, type(clstr.compute_nodes[0]))
        self.assertEqual(1, clstr.compute_nodes[0].n_jobs)


        ssh_hostname = 'cassia'
        compute_nodes = (ComputeNode(), SshComputeNode(ssh_hostname))
        clstr = Cluster(compute_nodes)
        filepath_list = [
            './___TestExperiment_Manager_{}.txt'.format(i)
            for i in range(10)
        ]
        commands = ['sleep 0.2; touch {}; '.format(fp) for fp in filepath_list]
        q_commands = Queue()
        for c in commands:
            q_commands.put(c)
        clstr.start(q_commands)
        clstr.wait_all()


        # ローカルとSSH先のどちらかにあるかのチェックと削除
        for filepath in filepath_list:
            local_check = os.path.exists(filepath)
            ssh_check_cmd = 'ssh ' + ssh_hostname + ' ls -l ' + filepath
            stdout = getoutput(ssh_check_cmd)
            ssh_check = not 'No such file' in stdout
            self.assertTrue(local_check ^ ssh_check)

            if local_check:
                os.remove(filepath)
            elif ssh_check:
                getoutput('ssh {} rm {}'.format(ssh_hostname, filepath))


if __name__ == '__main__':
    unittest.main()
