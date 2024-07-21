# -*- coding: utf-8 -*-
from typing import Any, Sequence

from .ParamEncoder import ParamEncoder
from .transform_param_value import transform_param_value


def make_param_str(
    params: dict | Sequence[Sequence[str | Any]],
    param_encoder: ParamEncoder | None = None,
    connector: str = "=",
    sep: str = ",",
) -> str:
    """パラメータ名と値がセットになっているdictかそれをリストに変換したものを入力として、１つの文字列を生成する関数
    Parameters
    ----------
    params: dict or 2d array-like
        入力となるパラメータ郡.dictの場合はパラメータを勝手にソーティングする。2d array-likeの場合はその順番で行う.
    param_encoder: an instance of ParamEncoder
        短縮文字列を使うParamEncoderオブジェクト. 指定しなければ内部でインスタンスを生成してそれを使う
    """
    if isinstance(params, dict):
        params = sorted(list(params.items()), key=lambda kv: str(kv[0]))

    if param_encoder is None:
        param_encoder = ParamEncoder()

    def make_element(k, v):
        return connector.join(
            [param_encoder.encode(k), transform_param_value(v)]
        )

    file_str = sep.join(make_element(k, v) for k, v in params)

    return file_str
