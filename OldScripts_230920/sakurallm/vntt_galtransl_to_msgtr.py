import json
import os


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

jsonjp_files = read_json_files("g\\jsonjp")
msg_tr = {}
name_tr = {}
for jsonjp in jsonjp_files:
    with open(jsonjp, encoding='utf8') as f:
        with open(jsonjp.replace('jp', 'cn'), encoding='utf8') as ftr:
            ori_data = json.load(f)
            tr_data = json.load(ftr)
            for i in range(len(ori_data)):
                # msg
                if not ori_data[i]['message'] in msg_tr:
                    msg_tr[ori_data[i]['message']] = tr_data[i]['message']
                # name
                if 'name' in ori_data[i]:
                    if not ori_data[i]['name'] in name_tr:
                        name_tr[ori_data[i]['name']] = tr_data[i]['name']

with open('g\\msg_tr.json', 'w', encoding='utf8') as f:
    f.writelines(json.dumps(msg_tr, ensure_ascii=False, indent=4))
with open('g\\name_tr.json', 'w', encoding='utf8') as f:
    f.writelines(json.dumps(name_tr, ensure_ascii=False, indent=4))

