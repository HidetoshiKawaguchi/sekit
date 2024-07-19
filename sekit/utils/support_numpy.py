# -*- coding:utf-8 -*-
from typing import Any

import numpy as np


# json.dumpsでdictをjson文字列へ変換するときに、numpyの型へ対応するためのメソッド
# (例)json.dumps(result, sort_keys = True, indent = 4, default=support_numpy )
def support_numpy(o: Any) -> float | int | list:
    if isinstance(o, np.float32):
        return float(o)
    if isinstance(o, np.int64):
        return int(o)
    if isinstance(o, np.ndarray):
        return list(o)
    raise TypeError(repr(o) + " is not JSON serializable")
