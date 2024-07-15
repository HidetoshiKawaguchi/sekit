# -*- coding: utf-8 -*-
import copy

import matplotlib.pyplot as plt


class Markers:
    def __init__(self):
        self.markers = [",", "o", "v", "^", "<", ">", "D", "p", "*"]
        self.index = 0

    def next(self):
        out = self.markers[self.index]
        self.index += 1
        if self.index == len(self.markers):
            self.index = 0
        return out


_init_key = "__init__"
_plots_key = "plots"
_special_keys = {_init_key, _plots_key}


def simple_matplot(
    param: dict,
    figsize: tuple = None,
    dpi: int = None,
    facecolor: str = None,
    edgecolor: str = None,
    linewidth: float = 0.0,
    frameon: bool = None,
    subplotpars=None,
    tight_layout: bool = None,
    constrained_layout=None,
) -> plt.Figure:
    param = copy.deepcopy(param)
    fig = plt.figure(
        figsize=figsize,
        dpi=dpi,
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=linewidth,
        frameon=frameon,
        subplotpars=subplotpars,
        tight_layout=tight_layout,
        constrained_layout=constrained_layout,
    )

    markers = Markers()
    ax = fig.add_subplot(111, **param.get(_init_key, dict()))
    for p in param.get(_plots_key, []):
        method = p.get("method", "plot")
        del p["method"]
        if not "marker" in p:
            p["marker"] = markers.next()
        if method == "plot":
            x, y = p["x"], p["y"]
            del p["x"]
            del p["y"]
            ax.plot(x, y, **p)
        else:
            getattr(ax, method)(**p)
    for k, p in param.items():
        if k in _special_keys:
            continue
        call = getattr(ax, k)
        if type(p) == dict:
            call(**p)
        elif type(p) == list:
            call(*p)
        else:
            call(p)
    return fig
