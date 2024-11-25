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


def process_json_files(file_paths):
    # 遍历文件夹下的所有文件和子文件夹
    for file_path in file_paths:
        print("I: processing " + file_path)
        new_data = []
        f = open(file_path, encoding='utf8')
        ori_data = json.load(f)
        for line in ori_data:
            new_line = {}
            for key, value in line.items():
                if key == "name":
                    cur_trans = get_trans_name(value)
                    new_line[key] = cur_trans
                elif key == "message":
                    cur_trans = get_trans_msg(value)
                    new_line[key] = cur_trans
                else:
                    print("W: unknown key: " + key)
                    new_line[key] = value
            new_data.append(new_line)
        # save new_data as json to ..\translated\{original_file_name}
        # new_file_path = os.path.join(os.path.dirname(os.path.dirname(file_path)), "jsoncn",
        #                              os.path.basename(file_path))
        new_file_path = file_path.replace("jsonjp", "jsoncn")
        if not os.path.exists(os.path.dirname(new_file_path)):
            os.makedirs(os.path.dirname(new_file_path))
        with open(new_file_path, 'w', encoding='utf8') as f3:
            f3.writelines(json.dumps(new_data, ensure_ascii=False, indent=4))


def get_trans_name(s):
    global name_dict
    # return s
    if s in name_dict:
        return name_dict[s]
    else:
        print("W: untranslated \"name\": " + s)
        return s


def get_trans_msg(s):
    global msg_dict
    if s in msg_dict:
        return msg_dict[s]
    else:
        print("W: untranslated \"message\": " + s)
        return s


def read_dicts():
    global name_dict
    global msg_dict
    f = open('name_tr.json', encoding='utf8')
    name_dict = json.load(f)
    f = open('msg_tr.json', encoding='utf8')
    msg_dict = json.load(f)


# main
name_dict = {}
msg_dict = {}
read_dicts()
file_paths = read_json_files("D:\\Temp\\230920_MTool_Trans\\sakurallm\\g\\jsonjp")
process_json_files(file_paths)
