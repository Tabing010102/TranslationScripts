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


def parse_content(text):
    if text == "\n":
        return text.encode("932")
    pos = 0
    text_bytes = b""
    # handle name
    if text[0] == '【':
        text_bytes += '【'.encode("936")
        while text[pos] != '】':
            pos += 1
        name_text = text[1:pos]
        if name_text.__contains__('＠'):
            names = name_text.split('＠')
            first = True
            for name in names:
                if first:
                    first = False
                else:
                    text_bytes += '＠'.encode("936")
                text_bytes += get_trans_name(name).encode("936")
        else:
            text_bytes += get_trans_name(name_text).encode("936")
        pos += 1
        text_bytes += '】'.encode("936")
    # handle content
    if text[-1] == '\n':
        text_bytes += get_trans_msg(text[pos:-1]).encode("936", )
        text_bytes += '\n'.encode("936")
    else:
        text_bytes += get_trans_msg(text[pos:]).encode("936", )
    return text_bytes


def get_trans_name(s: str):
    global name_dict
    if name_dict.__contains__(s):
        return name_dict[s]
    else:
        print("W: name not found: " + s)
        return s


def get_trans_msg(s: str):
    global msg_dict
    if msg_dict.__contains__(s):
        return msg_dict[s]
    else:
        print("W: msg not found: " + s)
        return s


def parse_line(line, f2):
    global f_err
    global pac_names
    len = line.__len__()
    pos = 0
    while pos < len:
        # skip command
        if line[pos] == '\\':
            o_pos = pos
            while pos < len and line[pos] != ')':
                pos += 1
            pos += 1
            try:
                cmd = line[o_pos:pos]
                is_contain = False
                for pac_name in pac_names:
                    if cmd.__contains__(pac_name):
                        is_contain = True
                        break
                if is_contain:
                    f2.write(cmd.encode("936"))
                else:
                    f2.write(cmd.encode("932"))
            except Exception as ex:
                cmd = line[o_pos:pos]
                # f_err.write("C: " + cmd + "\n")
                print(ex)
                cmds = cmd.split("・")
                first = True
                for cmd in cmds:
                    if first:
                        first = False
                    else:
                        f2.write("・".encode("932"))
                    f2.write(cmd.encode("936"))
        else:
            o_pos = pos
            while pos < len and line[pos] != '\\':
                pos += 1
            try:
                text_bytes = parse_content(line[o_pos:pos])
                f2.write(text_bytes)
            except Exception as ex:
                print(ex)


def load_csv_files(file_paths):
    for file_path in file_paths:
        f = open(file_path, encoding="932")
        f2 = open(file_path.replace("jp", "cn"), "wb")
        lines = f.readlines()
        for line in lines:
            if line == "\n":
                is_insert = False
            elif len(line.strip()) == 0:
                is_insert = False
            elif line.startswith("/"):
                is_insert = False
            elif not utils.is_cjk_str(line):
                is_insert = False
            else:
                is_insert = True
                parse_line(line, f2)
            if not is_insert:
                f2.write(line.encode("932"))
        f2.close()


f = open('name_tr.json', encoding='utf8')
name_dict = json.load(f)
f = open('msg_tr.json', encoding='utf8')
msg_dict = json.load(f)
f = open('pac_name.txt', encoding='utf8')
pac_names = []
for line in f.readlines():
    line = line.strip()
    name = line.replace(".ymv", "")
    if not pac_names.__contains__(name):
        pac_names.append(name)
f_err = open('err.txt', 'w', encoding='utf8')
file_paths = read_txt_files("D:\\Temp\\Pieces／揺り籠のカナリア\\scenariojp")
load_csv_files(file_paths)
