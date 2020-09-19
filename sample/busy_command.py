# -*- coding: utf-8 -*-
import sys, json, random
from time import sleep

if __name__ == '__main__':
    param = json.loads(sys.argv[1])
    v = random.randint(0, 3)
    for _ in range(v * (3 * 10**8)):
        pass
    print(param, v)
