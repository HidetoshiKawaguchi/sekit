# -*- coding: utf-8 -*-
import unittest
import os, sys, glob
import subprocess
base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.append(base)

from lib import SpartanController

class TestSpartan(unittest.TestCase):
    def test_spartan(self):
        python_command = os.path.join('spartan', 'test', 'command.py')
        input_dict = {
            'command': 'python ' + python_command,
            'param_grid': [
                {
                    'a': [0, 1, 2],
                    'b': ["hoge", "goro"]
                },
                {
                    'a': [3],
                    'b': ["giro"]
                }
            ],
            'hosts': [
                {'hostname': 'localhost', 'n_jobs': 1},
                {"hostname": 'cassia', 'n_jobs': 1}
            ],
            'option': {
                'n_seeds': 10
            }
        }
        hosts = input_dict['hosts']
        sc = SpartanController(hosts)

        command = input_dict['command']
        param_grid = input_dict['param_grid']
        option = input_dict['option']
        sc.exe(command, param_grid, **option)
        subprocess.run(['rsync', '-r',
                        'cassia:spartan/test/TestSpartan,a=*',
                        os.path.join(base, 'test')])
        filepath_pattern = os.path.join(base, 'test', 'TestSpartan,a=*')
        cnt = sum(1 for filepath in glob.glob(filepath_pattern))
        self.assertEqual(70, cnt)

        for filepath in glob.glob(filepath_pattern):
            os.remove(filepath)
        subprocess.run(['ssh', 'cassia', 'rm', 'spartan/test/TestSpartan,a=*'])

if __name__ == '__main__':
    # リモートホストのcassiaのホームディレクトリに本ディレクトリのクローンがあることが前提
    unittest.main()

