# -*- coding: utf-8 -*-


import os
import json
from config import json2js, js2json

def exec_node_cmd(ffrom, fto):
    if ffrom.endswith(".json"):
        os.system(f'node {json2js} {ffrom} {fto}')
    else:
        os.system(f'node {js2json} {ffrom} {fto}')


def dump_file(obj, fpath, method="w", **kwargs):
    file = open(fpath, method, encoding='utf8')
    if isinstance(obj, dict):
        json.dump(obj, file, **kwargs)
    else:
        file.write(obj)


def load_file(fpath, method="r", load=True, **kwargs):
    file = open(fpath, method, encoding='utf8')
    if load:
        return json.load(file, **kwargs)
    else:
        return file.read()