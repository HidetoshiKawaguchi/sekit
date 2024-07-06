from argparse import ArgumentParser

"""
ComputeNodeやSshComputeNodeのテストの際に呼び出す.
deviceの設定が割り振られるかをチェックするために使う
"""


parser = ArgumentParser()
parser.add_argument("outpath", type=str)
parser.add_argument("--_device", type=str)
args = parser.parse_args()
with open(args.outpath, "w") as f:
    f.write(args._device)
