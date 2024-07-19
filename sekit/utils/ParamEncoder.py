# -*- coding: utf-8 -*-
import re
from typing import Self, Sequence


class ParamEncoder:
    """実験用パラメータを短縮文字に変換するためのクラス"""

    def __init__(self, sep: str = "_") -> None:
        self.mapping_ = {}
        self.sep = sep

    def encode(self, param: str, sep: str | None = None) -> str:
        """与えられたパラメータをある規則に従って短縮形で返すメソッド. 内部状態にも依存する。
        '_'で単語を区切る.

        Parameters
        ----------
        param: String
            name of parameter
        Returns
        -------
        String
        """
        if sep is None:
            sep = self.sep

        if param in self.mapping_:  # ある場合はそのまま返す
            return self.mapping_[param]

        head = sep if re.match(r"{}".format(sep), param) else ""
        short_param = head + "".join(w[0] for w in param.split(sep) if w != "")

        if (
            short_param in self.mapping_.values()
        ):  # すでに同じ短縮版のパラメータがある場合
            cnt = 0
            for o in self.mapping_.values():
                if re.match(r"{}".format(short_param), o):
                    cnt += 1
            short_param += str(cnt)

        self.mapping_[param] = short_param

        return short_param

    def fit(self, params: Sequence[str]) -> Self:
        """パラメータのリストをインプットとして、短縮形を生成し保持する。

        Parameters
        ----------
        params: 1d array-like
            names of parameters for a experiment.
        Returns
        -------
        self
        """
        for p in params:
            self.encode(p, sep=self.sep)
        return self

    def transform(self, params: Sequence[str]) -> list[str]:
        """パラメータのリストを単語ごとにショート版に変換して返す

        Parameters
        ----------
        params: 1d array-like
            names of parameters for a experiment.
        Returns
        -------
        list
        """
        return [self.mapping_[p] for p in params]

    def fit_transform(self, params: Sequence[str]) -> list[str]:
        return self.fit(params).transform(params)

    def inverse_transform(self, s_params: Sequence[str]) -> list[str]:
        inverse_mapping = {v: k for k, v in self.mapping_.items()}
        return [inverse_mapping[sp] for sp in s_params]
