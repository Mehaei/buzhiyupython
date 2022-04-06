# -*- coding: utf-8 -*-

""" 函数调用还原 """
import execjs
from config import (
    ob_body_13_js,
    ob_step1_done_json,
    ob_step2_func_call_done_js,
    ob_step2_func_call_done_json,
    ob_step2_concat_str_js,
    ob_step2_concat_str_json
)
from tools import dump_file, load_file, exec_node_cmd


def call_function_reload(node, ctx):
    if type(node) == list:
        for item in node:
            call_function_reload(item, ctx)
        return
    elif type(node) != dict:
        return

    # 捕获一个 CallExpression 节点
    if node['type'] == 'CallExpression':
        try:
            if node['callee']['name'] == '$dbsm_0x42c3':  # 确认函数名
                arg_list = []
                for item in node['arguments']:  # 提取所有参数
                    if item['type'] != 'Literal':
                        break
                    arg_list.append(item['value'])
                else:
                    # 这里有一个隐藏的彩蛋,如果是用GBK去解码会触发报错,就会引起关注,就有可能发现这个彩蛋
                    value = ctx.call('$dbsm_0x42c3', *arg_list)
                    print(value)  # 这里加入一个print() 省的以为程序卡死了
                    new_node = {'type': 'Literal', 'value': value}
                    node.clear()
                    node.update(new_node)
                    return
        except KeyError:
            pass
    for key in node.keys():
        call_function_reload(node[key], ctx)

# 将拆分开的对象属性名称合并
def concat_obj_property_name(node):
    if type(node) == list:
        for item in node:
            concat_obj_property_name(item)
        return
    elif type(node) != dict:
        return

    # 捕获一个二元运算节点
    if node['type'] == 'BinaryExpression':
        if not (node['left']['type'] == 'Literal' and node['right']['type'] == 'Literal'):
            # 如果 其中有参数不是 字符 类型,则将两个参数都继续递归
            concat_obj_property_name(node['left'])
            concat_obj_property_name(node['right'])
        # 当两个参数分别的递归都完成, 参数类型最终都变为了 字符 类型,则可以合并,这样就实现了一连串的字符相加
        if node['left']['type'] == 'Literal' and node['right']['type'] == 'Literal':
            new_node = {'type': 'Literal', 'value': node['left']['value'] + node['right']['value']}
            node.clear()
            node.update(new_node)
            return

    for key in node.keys():
        concat_obj_property_name(node[key])


def func_call_revert():
    """ 字符串与数字回填[ok] """
    """ 函数调用还原[ok](此步骤及其耗时,估计是需要用python 频繁调用nodejs的原因) """
    data = load_file(ob_step1_done_json)
    ctx = execjs.compile(load_file(ob_body_13_js, load=False))
    call_function_reload(data, ctx)
    dump_file(data, ob_step2_func_call_done_json)
    exec_node_cmd(ob_step2_func_call_done_json, ob_step2_func_call_done_js)
    """ 对象调用还原[ok] """
    data = load_file(ob_step2_func_call_done_json)
    concat_obj_property_name(data)
    dump_file(data, ob_step2_concat_str_json)
    # 会生成一份用于观察分析下一步的临时文件 02_ob_concat_str.js/json
    exec_node_cmd(ob_step2_concat_str_json, ob_step2_concat_str_js)
