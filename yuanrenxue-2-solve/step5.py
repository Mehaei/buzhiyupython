# -*- coding: utf-8 -*-

""" 控制流平坦化 """
from config import (
    ob_step5_while_revert_js,
    ob_step5_while_revert_json,
    ob_step4_ifelse_revert_json
)
from tools import dump_file, load_file, exec_node_cmd


def sort_code(node):
    if type(node) == list:
        active = False
        try:
            # 捕获一个控制流节点(这是一个包含执行顺序和while节点的列表节点)
            if len(node) == 2:
                if node[1]['type'] == 'WhileStatement':
                    var1 = node[0]['expression']['expressions'][0]
                    var2 = node[0]['expression']['expressions'][1]
                    if var1['right']['type'] == 'CallExpression' and var2['right']['type'] == 'Literal':
                        active = True
            if not active:
                raise KeyError
        except (KeyError, TypeError):
            for item in node:
                sort_code(item)
            return
    elif type(node) == dict:
        for key in node.keys():
            sort_code(node[key])
        return
    else:
        return

    sort_list = var1['right']['callee']['object']['value'].split('|')  # 控制流程顺序列表
    cases_list = node[1]['body']['body'][0]['cases']  # 原控制流列表
    result_list = [cases_list[int(i)]['consequent'][0] for i in sort_list]  # 新的控制流列表

    node.clear()
    node.extend(result_list)
    for item in node:
        sort_code(item)


""" ********************************************************* """
def while_revert():
    # 生成基础文件
    """ 字符串与数字回填[ok] """
    """ 函数调用还原[ok] """
    """ 对象调用还原[ok] """
    """ 分支流程判断[ok] """
    """ 控制流平坦化[ok] """
    data = load_file(ob_step4_ifelse_revert_json)
    sort_code(data)
    dump_file(data, ob_step5_while_revert_json)
    exec_node_cmd(ob_step5_while_revert_json, ob_step5_while_revert_js)

