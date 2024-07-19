# -*- coding: utf-8 -*-
from itertools import product
from typing import Any, Generator, Sequence


def gen_param(
    source: dict[str, Any] | Sequence[Sequence[str | Any]]
) -> Generator[dict[str, Any], None, None]:
    if type(source) is dict:
        source = source.items()
    keys = tuple(v[0] for v in source)
    values = (v[1] for v in source)
    for v in product(*values):
        yield {keys[index]: value for index, value in enumerate(v)}
