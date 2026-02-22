# -*- coding: utf-8 -*-
from itertools import product
from typing import Any, Generator, Iterable, Sequence, cast


def gen_param(
    source: dict[str, Any] | Sequence[Sequence[str | Any]],
) -> Generator[dict[str, Any], None, None]:
    items: Iterable[Sequence[str | Any]]
    if type(source) is dict:
        items = source.items()
    else:
        items = source
    keys = tuple(cast(str, v[0]) for v in items)
    values = (v[1] for v in items)
    for v in product(*values):
        yield {keys[index]: value for index, value in enumerate(v)}
