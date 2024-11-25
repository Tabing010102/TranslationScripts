# 导入os和json模块
import os
import json

import utils


def read_json_files(folder):
    # 创建一个空列表，用于存储文件路径
    file_paths = []
    # 遍历文件夹下的所有文件和子文件夹
    for root, dirs, files in os.walk(folder):
        # 遍历所有文件
        for file in files:
            if file.endswith(".json"):
                file_paths.append(os.path.join(root, file))
    # 返回文件路径列表
    return file_paths


def load_json_files(file_paths, name_dict, msg_dict):
    # 遍历文件夹下的所有文件和子文件夹
    for file_path in file_paths:
        f = open(file_path, encoding='utf8')
        ori_data = json.load(f)
        for line in ori_data:
            # line is a dict
            # if dict contains "name" key
            if "name" in line:
                name_dict[line["name"]] = line["name"]
            # if dict contains "msg" key
            if "message" in line:
                msg_dict[line["message"]] = line["message"]


file_paths = read_json_files("g\\jsonjp")
name_dict = {}
msg_dict = {}
load_json_files(file_paths, name_dict, msg_dict)
with open('g/name.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(name_dict, ensure_ascii=False, indent=4))
with open('g/msg.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(msg_dict, ensure_ascii=False, indent=4))
