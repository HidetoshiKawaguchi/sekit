# -*- coding: utf-8 -*-
import sys, json, random
from time import sleep

if __name__ == '__main__':
    param = json.loads(sys.argv[1])
    sleep(random.randint(0, 3))
    print(param, type(param))





