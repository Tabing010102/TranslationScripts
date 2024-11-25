# 导入os和json模块
import csv
import os
import json

import utils


def read_txt_files(folder):
    file_paths = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(".txt"):
                file_paths.append(os.path.join(root, file))
    return file_paths


def parse_content(text, name_dict, msg_dict):
    if text == "\n":
        return
    pos = 0
    if text[0] == '【':
        while text[pos] != '】':
            pos += 1
        name_text = text[1:pos]
        if name_text.__contains__('＠'):
            names = name_text.split('＠')
            for name in names:
                name_dict[name] = name
        else:
            name_dict[name_text] = name_text
        pos += 1
    if text[-1] == '\n':
        msg_dict[text[pos:-1]] = text[pos:-1]
    else:
        msg_dict[text[pos:]] = text[pos:]

def parse_line(line, name_dict, msg_dict):
    len = line.__len__()
    pos = 0
    while pos < len:
        # skip command
        if line[pos] == '\\':
            while pos < len and line[pos] != ')':
                pos += 1
            pos += 1
        else:
            o_pos = pos
            while pos < len and line[pos] != '\\':
                pos += 1
            parse_content(line[o_pos:pos], name_dict, msg_dict)


def load_txt_files(file_paths, name_dict, msg_dict):
    for file_path in file_paths:
        f = open(file_path, encoding="932")
        lines = f.readlines()
        for line in lines:
            if line == "\n":
                continue
            elif len(line.strip()) == 0:
                continue
            elif line.startswith("/"):
                continue
            elif not utils.is_cjk_str(line):
                continue
            else:
                parse_line(line, name_dict, msg_dict)


file_paths = read_txt_files("D:\\Temp\\Pieces／揺り籠のカナリア\\scenariojp")
name_dict = {}
msg_dict = {}
load_txt_files(file_paths, name_dict, msg_dict)
with open('name.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(name_dict, ensure_ascii=False, indent=4))
with open('msg.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(msg_dict, ensure_ascii=False, indent=4))
