# -*- coding: utf-8 -*-
import sys, json, random

def exe(a: float, b: str, _seed: int) -> str:
    random.seed(_seed)
    s = 0
    c = random.randint(1, 3)
    for _ in range(int(a * (c * 10**8))):
        s += a
    out = '{}-{} (a={}, b={}, _seed={})'.format(b, s, a, b, _seed)
    return out

if __name__ == '__main__':
    param = json.loads(sys.argv[1])
    a = param['a']
    b = param['b']
    _seed = param['_seed']
    print(exe(a, b, _seed))
