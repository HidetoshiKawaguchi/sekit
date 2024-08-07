# -*- coding: utf-8 -*-
import json
import os
import os.path as op
import time
import traceback
from typing import Any, Callable, Literal, Sequence, TypeAlias

import pandas as pd

from ..utils import (
    ParamEncoder,
    convert_param_to_list,
    make_param_str,
    support_numpy,
)

EioOutput: TypeAlias = (
    dict[str, Any] | pd.DataFrame | tuple[dict | pd.DataFrame]
)


def _make_output_dir(
    mkdir: Literal["shallow", "deep", "on", "off"],
    out_dir: str,
    param_list: list[list[str, Any]],
    param_encoder: ParamEncoder,
    tail_param: Sequence[str],
) -> str:
    if mkdir not in {"shallow", "deep", "on", "off"}:
        err_msg = (
            f"Invalid value for 'mkdir': {mkdir}."
            + " Allowed values are 'shallow', 'deep', 'on', 'off'."
        )
        raise ValueError(err_msg)

    if mkdir == "shallow":
        dirname_param_str = make_param_str(
            param_list[: -len(tail_param)],
            param_encoder=param_encoder,
            sep=",",
        )
        output_dir = op.join(out_dir, dirname_param_str)
    elif mkdir == "deep":
        dirname_param_str = make_param_str(
            param_list[: -len(tail_param)],
            param_encoder=param_encoder,
            sep="/",
        )
        output_dir = op.join(out_dir, dirname_param_str)
    elif mkdir == "on" or mkdir == "off":
        output_dir = out_dir
    return output_dir


def _make_output_info(
    out_dir: str,
    kargs: dict[Any, Any],
    tail_param: Sequence[str],
    mkdir: Literal["shallow", "deep", "on", "off"],
) -> tuple[str, str]:
    # パラメータの順番を整えるためにリスト化。[key, value]を要素として持つ
    param_list = convert_param_to_list(kargs, tail_param=tail_param)
    param_encoder = (
        ParamEncoder()
    )  # 後で出力ディレクトリのパスを作るためにも使う
    param_encoder.fit([p[0] for p in param_list])
    filename_param_str = make_param_str(
        param_list, param_encoder=param_encoder, sep=","
    )
    output_dir = _make_output_dir(
        mkdir, out_dir, param_list, param_encoder, tail_param
    )
    return output_dir, filename_param_str


def eio(
    out_dir: str = "./",
    header: str | None = None,
    param_flag: bool = True,
    header_flag: bool = True,
    process_time: float = True,
    trace_back: bool = False,
    display: bool = True,
    error_display: bool = False,
    sort_keys: bool = True,
    ensure_ascii: bool = False,
    mkdir: Literal["shallow", "deep", "on", "off"] = "off",
    indent: int = 4,
    default: Callable[[Any], float | int | list] = support_numpy,
    tail_param: Sequence[str] = ("_seed",),
) -> Callable[[Callable[..., EioOutput]], Callable[..., EioOutput]]:
    def _eio(func: Callable[..., EioOutput]) -> Callable[..., EioOutput]:
        def _decorated_func(
            *args: tuple[...], **kargs: dict[str, Any]
        ) -> EioOutput:
            l_header = func.__name__ if header is None else header
            start_time = time.time()
            if trace_back:
                result = func(*args, **kargs)
            else:
                try:
                    result = func(*args, **kargs)
                except Exception as e:
                    result = {
                        "_error_type": str(type(e)),
                        "_error_args": str(e.args),
                        "_error_self": str(e),
                        "_error_traceback": traceback.format_exc(),
                    }
            process_time = time.time() - start_time

            # 出力ディレクトリとファイル名の文字列の作成
            # - out_dir: 出力先のディレクトリ
            # - kargs: 実験用関数のパラメータ(dict)
            # - tail_param: 文字列生成時に末尾に持ってくるパラメータ
            # - mkdir: ディレクトリの作成モード
            output_dir, filename_param_str = _make_output_info(
                out_dir, kargs, tail_param, mkdir
            )
            if mkdir == "on" or mkdir == "shallow" or mkdir == "deep":
                os.makedirs(output_dir, exist_ok=True)

            # 出力ディレクトリとファイル名の文字列を使って、実際に書き込む
            # JSON用の書き込みメソッド
            def write_json(result, cnt=0):
                if header_flag:
                    result["_header"] = l_header
                if param_flag:
                    result["_param"] = kargs
                if process_time:
                    result["_process_time"] = process_time
                if (
                    error_display and "_error_type" in result
                ):  # エラーが起きたとき
                    print("error: " + str(result["_param"]))
                    print(result["_error_traceback"])
                result_json_str = json.dumps(
                    result,
                    sort_keys=sort_keys,
                    ensure_ascii=ensure_ascii,
                    indent=indent,
                    default=default,
                )
                tail = "" if cnt == 0 else ("_" + str(cnt))
                filename = "{},{}{}.json".format(
                    l_header, filename_param_str, tail
                )
                outpath = op.join(output_dir, filename)
                with open(outpath, "w", encoding="utf-8") as f:
                    f.write(result_json_str)

            # CSV用の書き込みメソッド
            def write_csv(df, cnt=0):
                tail = "" if cnt == 0 else ("_" + str(cnt))
                filename = "{},{}{}.csv".format(
                    l_header, filename_param_str, tail
                )
                outpath = op.join(output_dir, filename)
                df.to_csv(outpath)

            if isinstance(result, dict):
                write_json(result)
            elif isinstance(result, pd.DataFrame):
                write_csv(result)
            elif hasattr(result, "__iter__"):
                dict_cnt, df_cnt = 0, 0
                for res in result:
                    if isinstance(res, dict):
                        write_json(res, dict_cnt)
                        dict_cnt += 1
                    if isinstance(res, pd.DataFrame):
                        write_csv(res, df_cnt)
                        df_cnt += 1
            if display:
                minute = round(process_time / 60.0, 2)
                print("[{}m] finished: {}".format(minute, filename_param_str))
            return result

        return _decorated_func

    return _eio
