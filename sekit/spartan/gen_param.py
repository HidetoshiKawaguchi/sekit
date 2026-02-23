# -*- coding: utf-8 -*-
from itertools import product
from typing import Any, Generator, Iterable


def gen_param(
    source: dict[str, Any] | Iterable[tuple[str, Any]],
) -> Generator[dict[str, Any], None, None]:
    items: Iterable[tuple[str, Any]] = (
        source.items() if isinstance(source, dict) else source
    )
    keys = tuple(v[0] for v in items)
    values = (v[1] for v in items)
    for v in product(*values):
        yield {keys[index]: value for index, value in enumerate(v)}
