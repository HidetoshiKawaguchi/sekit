# -*- coding: utf-8 -*-
from typing import Any, Sequence


def convert_param_to_list(
    param: dict[str, Any], tail_param: Sequence[str] = ("_seed_index", "_seed")
) -> list[list[str, Any]]:
    """パラメータのdictを並びかえて, リスト形式にするジェネレータ関数.
    Parameters
    ----------
    param: dict
        keyがパラメータ名, valueがそのパラメータの値を示すdict型の関数
    tail_param: array-like
        返り値のおしりに持ってきたいパラメータのリスト
    Return
    ------
    2d array-like
    """
    param_list = sorted(list(param.items()), key=lambda kv: str(kv[0]))
    head_params_list = [kv for kv in param_list if kv[0] not in tail_param]
    tail_param_list = [
        [para, param.get(para)]
        for para in tail_param
        if param.get(para) is not None
    ]

    return head_params_list + tail_param_list
