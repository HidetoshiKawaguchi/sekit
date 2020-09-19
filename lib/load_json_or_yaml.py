# -*- coding: utf-8 -*-
import os.path as op
import json, yaml

def load_yaml_or_json(filepath):
    basename = op.basename(filepath)
    ext = op.splitext(basename)[1]
    with open(filepath, 'r') as f:
        if ext == 'json':
            return json.load(f)
        else: #yaml
            return yaml.load(f, Loader=yaml.SafeLoader)
