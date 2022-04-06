# -*- coding: utf-8 -*-

""" 对象调用还原 """
import copy
import sys
from config import (
    ob_step3_obj_call_done_js,
    ob_step3_obj_call_done_json,
    ob_step3_spawn_obj_map_json,
    ob_step3_spawn_obj_map_js,
    ob_step2_concat_str_json
)
from tools import dump_file, load_file, exec_node_cmd


# 构造对象属性字典
obj_property_dict = {}
obj_name_list = []


def get_property_dicet(node):
    # 所有对象申明时都是: XXXX = {}, 然后使用 XXXX['xxxx'] = XXXXXXX 来添加属性
    if type(node) == list:
        for item in node:
            get_property_dicet(item)
        return
    elif type(node) != dict:
        return

    # 捕获一个表达式序列
    if node['type'] == 'SequenceExpression':
        for i in range(- len(node['expressions']), 0, 1):  # 正向遍历列表,并且可以删除元素的方式
            item = node['expressions'][i]
            # 捕获一个(变量/属性)申明节点
            if item['type'] == 'AssignmentExpression':
                # 是一个变量申明
                if item['left']['type'] == 'Identifier':
                    # 申明的是一个空对象
                    if item['right']['type'] == 'ObjectExpression' and item['right']['properties'] == []:
                        obj_property_dict[item['left']['name']] = {}
                        obj_name_list.append(item['left']['name'])
                        del node['expressions'][i]
                        continue
                    # 申明 一个变量指向另一个变量 例: _0x5500bb = _0x434ddb,
                    elif item['right']['type'] == 'Identifier':
                        if item['right']['name'] in obj_property_dict:
                            obj_property_dict[item['left']['name']] = obj_property_dict[item['right']['name']]
                            obj_name_list.append(item['left']['name'])
                            del node['expressions'][i]
                            continue
                # 是一个属性申明
                elif item['left']['type'] == 'MemberExpression':
                    obj_name = item['left']['object']['name']
                    try:
                        obj_property_name = item['left']['property']['value']
                        obj_property_dict[obj_name][obj_property_name] = item['right']
                        del node['expressions'][i]
                        continue
                    except KeyError:
                        pass

            for key in item.keys():
                get_property_dicet(item[key])

    for key in node.keys():
        get_property_dicet(node[key])


# 对象调用还原
def obj_property_reload(node):
    if type(node) == list:
        for item in node:
            obj_property_reload(item)
        return
    elif type(node) != dict:
        return

    # 捕获一个属性调用节点
    if node['type'] == 'MemberExpression':
        try:
            obj_name = node['object']['name']
            obj_property = node['property']['value']
            new_node = obj_property_dict[obj_name][obj_property]
            if new_node['type'] != 'FunctionExpression':
                node.clear()
                node.update(new_node)
                obj_property_reload(node)
        except KeyError:
            pass
    try:
        # 捕获一个函数调用节点,且子节点callee的类型是一个MemberExpression
        if node['type'] != 'CallExpression' or node['callee']['type'] != 'MemberExpression':
            raise KeyError
        obj_name = node['callee']['object']['name']  # 获取对象名称
        obj_property_name = node['callee']['property']['value']  # 获取需要调用的对象属性名称
        function_node = obj_property_dict[obj_name][obj_property_name]  # 获取函数定义节点,即对象的属性值(该属性值是一个函数定义)
    except KeyError:
        for key in node.keys():
            obj_property_reload(node[key])
        return

    # 获取形参
    param_list = [item['name'] for item in function_node['params']]
    # 获取实参
    argument_list = node['arguments']
    # 形成形参与实参的对比关系,如此,可以适应形参位置发生变化
    param_argument_dict = dict(zip(param_list, argument_list))

    # 拷贝一份函数节点的返回值子节点
    return_node = copy.deepcopy(function_node['body']['body'][0])
    if return_node['type'] != 'ReturnStatement':
        print(f'意料之外的函数节点,拥有超过一行的函数体: {function_node}')
        sys.exit()

    # 使用实参替换返回值节点中的形参,然后用返回值节点,替换掉整个函数调用node节点
    if return_node['argument']['type'] == 'Literal' or return_node['argument']['type'] == 'MemberExpression':
        # 直接替换
        node.clear()
        node.update(return_node['argument'])
    elif return_node['argument']['type'] == 'BinaryExpression' or return_node['argument']['type'] == 'LogicalExpression':
        if return_node['argument']['left']['type'] == 'Identifier':
            return_node['argument']['left'] = param_argument_dict[return_node['argument']['left']['name']]
        if return_node['argument']['right']['type'] == 'Identifier':
            return_node['argument']['right'] = param_argument_dict[return_node['argument']['right']['name']]
        node.clear()
        node.update(return_node['argument'])
    elif return_node['argument']['type'] == 'CallExpression':
        if return_node['argument']['callee']['type'] != 'MemberExpression':
            function_name = return_node['argument']['callee']['name']
            if function_name in param_argument_dict:
                return_node['argument']['callee'] = param_argument_dict[function_name]
        for i in range(len(return_node['argument']['arguments'])):
            if return_node['argument']['arguments'][i]['type'] == 'Identifier':
                argument_name = return_node['argument']['arguments'][i]['name']
                return_node['argument']['arguments'][i] = param_argument_dict[argument_name]
        node.clear()
        node.update(return_node['argument'])
    else:
        print(f'意料之外的函数返回值类型: {return_node}')
        sys.exit()
    # 替换完成后,将自身继续递归
    obj_property_reload(node)
    return


""" ********************************************************* """


def obj_call_revert():
    # 生成基础文件

    """ 字符串与数字回填[ok] """
    """ 函数调用还原[ok] """
    """ 对象调用还原[ok] """
    data = load_file(ob_step2_concat_str_json)
    get_property_dicet(data)
    dump_file(data, ob_step3_spawn_obj_map_json)
    exec_node_cmd(ob_step3_spawn_obj_map_json, ob_step3_spawn_obj_map_js)
    # 验证对象名称是否有重复,如果有,就只能将JS分成单个部分传入还原
    # print(len(obj_property_dict))
    # print(len(obj_name_list))

    obj_property_reload(data)
    dump_file(data, ob_step3_obj_call_done_json)
    exec_node_cmd(ob_step3_obj_call_done_json, ob_step3_obj_call_done_js)