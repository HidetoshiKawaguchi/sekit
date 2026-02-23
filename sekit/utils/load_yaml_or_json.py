# -*- coding: utf-8 -*-
import json
import os.path as op
from typing import Any, cast

import yaml


def load_yaml_or_json(filepath: str) -> dict[str, Any]:
    basename = op.basename(filepath)
    ext = op.splitext(basename)[1]
    with open(filepath, "r") as f:
        if ext == ".json":
            return cast(dict[str, Any], json.load(f))
        else:  # yaml
            return cast(dict[str, Any], yaml.safe_load(f))
