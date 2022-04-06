# -*- coding: utf-8 -*-

import json
import os
import execjs
import requests
from step1 import string_and_number_revert
from step2 import func_call_revert
from step3 import obj_call_revert
from step4 import ifelse_revert
from step5 import while_revert
from config import (
    ob_source_js,
    ob_body_46_json,
    target_url,
    ob_source_json,
    ob_body_13_json,
    ob_body_13_js,
    ob_body_46_js,
    submit_result_url
)
from tools import exec_node_cmd, dump_file, load_file


def download_ob_source_js():
    if os.path.exists(ob_source_js):
        return
    res = requests.get(target_url)
    dump_file(res.content[8:-9], ob_source_js, method="wb")
    exec_node_cmd(ob_source_js, ob_source_json)
    # 总文件分为6个部分,将前三个与后三个部分拆开
    node = load_file(ob_source_json)
    left_3_node = {
        'type': 'Program',
        'body': node['body'][:3],
        'sourceType': 'script'
    }
    right_3_node = {
        'type': 'Program',
        'body': node['body'][3:],
        'sourceType': 'script'
    }
    json.dump(left_3_node, ob_body_13_json)
    json.dump(right_3_node, ob_body_46_json)
    exec_node_cmd(ob_body_13_json, ob_body_13_js)
    exec_node_cmd(ob_body_46_json, ob_body_46_js)


def submit_result():
    js_data = load_file("ast_revert_done.js", load=False)
    total = 0
    for i in range(1, 6):
        params = (
            ("page", i),
        )
        cookies = {
            "m": execjs.eval(js_data)
        }
        headers = {
            'User-Agent': 'yuanrenxue.project',
            }
        response = requests.get(submit_result_url, headers=headers, params=params, cookies=cookies)
        data = response.json()["data"]
        for d in data:
            total += d["value"]

    print(total)
    return total


if __name__ == "__main__":
    # download_ob_source_js()
    # string_and_number_revert()
    # func_call_revert()
    # obj_call_revert()
    # ifelse_revert()
    # while_revert()
    submit_result()
