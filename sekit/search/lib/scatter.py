# -*- coding: utf-8 -*-
import copy
import os
import os.path as op
import sys

sys.path.append(op.join(op.dirname(op.abspath(__file__)), "..", ".."))
from itertools import combinations, product

import numpy as np
from jymatplot.lib import simple_matplot
from utils import make_param_str


def _plot_dict(title, xlabel, ylabel):
    return {
        "title": title,
        "xlabel": xlabel,
        "ylabel": ylabel,
        "grid": {"color": "#DDDDDD"},
        "legend": {
            "bbox_to_anchor": [1.05, 1.0],
            "loc": "upper left",
            "ncol": 1,
            "borderaxespad": 0,
        },
        # 'legend': {},
        "plots": [],
    }


def _output_columns(df, sep="|", target_types=[np.float64]):
    sep_index = list(df.columns).index(sep)
    columns = np.array(df.columns)[sep_index + 1 :]
    output_columns = [c for c in columns if df[c].dtype in target_types]
    return output_columns


def _make_params(df, keys):
    key_dict = {k: list(set(df[k])) for k in keys}
    return [[[k, v] for v in vs] for k, vs in key_dict.items()]


def scatter(
    in_df,
    figure_keys,
    input_keys,
    output="./",
    sep="|",
    dpi=None,
    display=False,
):
    fig_params = _make_params(in_df, figure_keys)

    for fig_param in product(*fig_params):
        df = in_df[in_df.columns]
        for key, val in fig_param:
            df = df[df[key] == val]
            del df[key]
        header = make_param_str(fig_param)
        output_columns = _output_columns(df, sep)
        for o1, o2 in combinations(output_columns, 2):
            plot_dict = _plot_dict(title=header, xlabel=o1, ylabel=o2)
            input_params = _make_params(df, input_keys)
            for input_param in product(*input_params):
                o_df = df[df.columns]
                for key, val in input_param:
                    o_df = o_df[o_df[key] == val]
                plot_dict["plots"].append(
                    {
                        "x": o_df[o1].to_numpy(),
                        "y": o_df[o2].to_numpy(),
                        "label": make_param_str(input_param),
                        "method": "scatter",
                    }
                )
            if len(plot_dict["plots"]) > 0:
                fig = simple_matplot(plot_dict, dpi=dpi)
                filename = "{}-{},{}.png".format(header, o1, o2)
                filepath = op.join(output, filename)
                fig.savefig(filepath, bbox_inches="tight")
                if display:
                    print(filepath)
