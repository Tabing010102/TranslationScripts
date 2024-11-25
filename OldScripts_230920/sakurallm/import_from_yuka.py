# 导入os和json模块
import csv
import os
import json

import utils


def read_csv_files(folder):
    # 创建一个空列表，用于存储文件路径
    file_paths = []
    # 遍历文件夹下的所有文件和子文件夹
    for root, dirs, files in os.walk(folder):
        # 遍历所有文件
        for file in files:
            if file.endswith(".csv"):
                file_paths.append(os.path.join(root, file))
    # 返回文件路径列表
    return file_paths


def load_csv_files(file_paths, name_dict, msg_dict, sw_dict):
    # 遍历文件夹下的所有文件和子文件夹
    for file_path in file_paths:
        f = open(file_path, encoding='utf8')
        # read csv
        reader = csv.reader(f)
        for row in reader:
            try:
                if len(row[2].strip()) == 0:
                    continue
                if row[0] == "ID":
                    continue
                if row[0].startswith("N"):
                    name_dict[row[2]] = row[2]
                elif row[0].startswith("L"):
                    msg_dict[row[2]] = row[2]
                elif row[0].startswith("S"):
                    sw_dict[row[2]] = row[2]
                else:
                    print("W: unknown prefix, row[0] = {}".format(row[0]))
            except:
                continue


# file_paths = read_csv_files("D:\\Temp\\ラブラブル～lover able～\\DATA01JP")
file_paths = read_csv_files("D:\\Temp\\同棲ラブラブル\\DATA01JP")
name_dict = {}
msg_dict = {}
sw_dict = {}
load_csv_files(file_paths, name_dict, msg_dict, sw_dict)
with open('name.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(name_dict, ensure_ascii=False, indent=4))
with open('msg.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(msg_dict, ensure_ascii=False, indent=4))
with open('sw.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(sw_dict, ensure_ascii=False, indent=4))
