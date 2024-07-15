# -*- coding: utf-8 -*-
import json
import os.path as op

import yaml


def load_yaml_or_json(filepath):
    basename = op.basename(filepath)
    ext = op.splitext(basename)[1]
    with open(filepath, "r") as f:
        if ext == ".json":
            return json.load(f)
        else:  # yaml
            return yaml.safe_load(f)
