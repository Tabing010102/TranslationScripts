import json
import os


tr_dict = {}


def read_txt_files(folder):
    # 创建一个空列表，用于存储文件路径
    file_paths = []
    # 遍历文件夹下的所有文件和子文件夹
    for root, dirs, files in os.walk(folder):
        # 遍历所有文件
        for file in files:
            if file.endswith(".txt"):
                file_paths.append(os.path.join(root, file))
    # 返回文件路径列表
    return file_paths


def insert_into_files(file_path, folder_path):
    f = open(file_path, encoding='utf-16')
    lines = f.readlines()
    lines2 = []
    for line in lines:
        line = line.strip()
        if line == '':
            lines2.append('\n')
            continue
        line = line.replace('\\n', '\\r\\n')
        endswith_at = False
        if line.endswith('\\@'):
            endswith_at = True
            line = line[:-2]
        if line in tr_dict.keys():
            line2 = tr_dict[line]
            if endswith_at:
                line2 = line2 + '\\@'
            line2 = line2 + '\n'
            lines2.append(line2)
        else:
            print('W: untranslated line: ' + line)
            line2 = line + '\n'
            lines2.append(line2)
    f2 = open(os.path.join(folder_path, os.path.basename(file_path)), "w", encoding='utf-8')
    f2.writelines(lines2)
    f2.close()


def read_json():
    global tr_dict
    f = open('msg_tr.json', encoding='utf8')
    tr_dict = json.load(f)
    f = open('name_tr.json', encoding='utf8')
    name_dict = json.load(f)
    for k, v in name_dict.items():
        tr_dict[k] = v


if __name__ == '__main__':
    read_json()
    base_folder_path = 'D:\\Temp\\ここから夏のイノセンス！\\ineditor'
    file_paths = read_txt_files(os.path.join(base_folder_path, 'txtjp'))
    for file_path in file_paths:
        insert_into_files(file_path, os.path.join(base_folder_path, 'txtcn'))
