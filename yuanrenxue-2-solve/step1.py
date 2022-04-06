# -*- coding: utf-8 -*-

import copy
import sys
from config import ob_body_46_json, ob_step1_done_json
from tools import dump_file, load_file


# 提取变量与字符串的映射
def get_string_number_dict(node):
    # 后三部分,每一部分都有这样的结构,而且变量名称有重复,必须分开做
    string_number_dict = {}

    try:
        # 第四部分路径
        expressions_list = node['expression']['callee']['body']['body'][0]['expression']['expressions']
    except TypeError:
        # 第五部分路径
        expressions_list = node['body']['body'][0]['expression']['expressions']
    except KeyError:
        # 第六部分路径
        expressions_list = node['expression']['arguments'][0]['body']['body'][0]['expression']['expressions']

    for item in expressions_list:
        # print(json.dumps(item, indent=4))
        if item['type'] != 'AssignmentExpression':
            # 跳过不是赋值表达式的节点
            continue
        if item['left']['type'] == 'Identifier':
            if item['right']['type'] == 'Literal':
                string_number_dict[item['left']['name']] = item['right']
            elif item['right']['type'] == 'BinaryExpression':
                # 二进制表达式
                left = string_number_dict[item['right']['left']['name']]
                right = item['right']['right']
                try:
                    new_node = copy.deepcopy(right)
                    # 计算出表达式的值
                    new_node['value'] = eval(f'{left["value"]} {item["right"]["operator"]} {right["value"]}')
                    string_number_dict[item['left']['name']] = new_node
                except TypeError:
                    print(item['right'])
                    sys.exit()
    return string_number_dict


# 将调用这些变量的地方进行还原
def string_number_reload(node, string_number_dict):

    # 一次只能还原一个部分
    if type(node) == list:
        for item in node:
            string_number_reload(item, string_number_dict)
        return
    elif type(node) != dict:
        return
    # 调用这些变量的地方都是实参
    try:
        for i in range(len(node['arguments'])):
            if node['arguments'][i]['type'] == 'Identifier':
                try:
                    # 捕获前面参数不匹配,而后面参数匹配的情况
                    node['arguments'][i] = string_number_dict[node['arguments'][i]['name']]
                except KeyError:
                    pass
        else:
            raise KeyError
    except KeyError:
        for key in node.keys():
            string_number_reload(node[key], string_number_dict)
        return


# 删除变量与字符串映射的节点
def del_string_number_node(node):
    try:
        expressions_list = node['expression']['callee']['body']['body'][0]['expression']['expressions']
    except TypeError:
        expressions_list = node['body']['body'][0]['expression']['expressions']
    except KeyError:
        # 第五部分路径
        expressions_list = node['expression']['arguments'][0]['body']['body'][0]['expression']['expressions']

    for i in range(len(expressions_list) - 1, -1, -1):
        if expressions_list[i]['type'] != 'AssignmentExpression':
            # 跳过不是赋值表达式的节点
            continue
        if expressions_list[i]['left']['type'] == 'Identifier' and expressions_list[i]['right']['type'] in (
                'Literal', 'BinaryExpression'):

            del expressions_list[i]


""" ********************************************************* """


def string_and_number_revert():
    """ 字符串与数字回填[ok] """
    data = load_file(ob_body_46_json)
    for item in data['body']:    # 将每一部分,分别做回填
        string_number_dict = get_string_number_dict(item)
        string_number_reload(item, string_number_dict)
        del_string_number_node(item)
    dump_file(data, ob_step1_done_json)