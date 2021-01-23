# -*- coding: utf-8 -*-
import copy
import matplotlib.pyplot as plt

def simple_matplot(param:dict,
                   figsize:tuple = None,
                   dpi:int = None,
                   facecolor:str = None,
                   edgecolor:str = None,
                   linewidth:float = 0.0,
                   frameon:bool = None,
                   subplotpars = None,
                   tight_layout:bool = None,
                   constrained_layout = None) -> plt.Figure:
    param = copy.deepcopy(param)
    fig = plt.figure(figsize=figsize, dpi=dpi, facecolor=facecolor,
                     edgecolor=edgecolor, linewidth=linewidth,
                     frameon=frameon, subplotpars=subplotpars,
                     tight_layout=tight_layout,
                     constrained_layout=constrained_layout)

    plots = param.get('plots', [])
    del param['plots']

    legend = param.get('legend', None)
    if legend is not None:
        del param['legend']
    grid = param.get('grid', None)
    if grid is not None:
        del param['grid']

    ax = fig.add_subplot(111, **param)
    for p in plots:
        method = p.get('method', 'plot')
        del p['method']
        if method == 'plot':
            x, y = p['x'], p['y']
            del p['x']
            del p['y']
            ax.plot(x, y, **p)
        else:
            getattr(ax, method)(**p)

    if legend is not None:
        ax.legend(**legend)
    if grid is not None:
        ax.grid(**grid)
        ax.set_axisbelow(True)

    return fig
