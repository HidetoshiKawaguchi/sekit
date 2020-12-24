# -*- coding: utf-8 -*-
import sys, json, random
if __name__ == '__main__':
    param = json.loads(sys.argv[1])
    v = random.random()
    for _ in range(int(v * (3 * 10**8))):
        pass
    print(param, v)
