# -*- coding: utf-8 -*-

""" 分支流程判断 """
import sys
from config import (
    ob_step3_obj_call_done_json,
    ob_step4_ifelse_revert_js,
    ob_step4_ifelse_revert_json
)
from tools import dump_file, load_file, exec_node_cmd

operator_dict = {'===': '==', '!==': '!='}
def if_reload(node):
    if type(node) == list:
        for item in node:
            if_reload(item)
        return
    elif type(node) != dict:
        return

    # 捕获一个分支语句节点
    if node['type'] == 'IfStatement':
        if node['test']['type'] == 'BinaryExpression':
            # 判断分支条件是否可执行
            if node['test']['left']['type'] == 'Literal' and node['test']['right']['type'] == 'Literal':
                # 获取分支节点
                consequent = node['consequent']
                alternate = node['alternate']
                try:
                    if eval(f"'{node['test']['left']['value']}' {operator_dict[node['test']['operator']]} '{node['test']['right']['value']}'"):
                        node.clear()
                        node.update(consequent)
                    else:
                        node.clear()
                        node.update(alternate)
                except KeyError:
                    print(f'意料之外的分支运算符号: {node}')
                    sys.exit()
                else:
                    if_reload(node)

    for key in node.keys():
        if_reload(node[key])


""" ********************************************************* """
def ifelse_revert():
    # 生成基础文件
    """ 字符串与数字回填[ok] """
    """ 函数调用还原[ok] """
    """ 对象调用还原[ok] """
    """ 分支流程判断[ok] """
    data = load_file(ob_step3_obj_call_done_json)
    if_reload(data)
    dump_file(data, ob_step4_ifelse_revert_json)
    exec_node_cmd(ob_step4_ifelse_revert_json, ob_step4_ifelse_revert_js)
