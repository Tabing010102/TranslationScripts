import json
import os

from sakurallm.sakura import sakura_strip


def read_json_files(folder, file_name="sr.json"):
    # 创建一个空列表，用于存储文件路径
    file_paths = []
    # 遍历文件夹下的所有文件和子文件夹
    for root, dirs, files in os.walk(folder):
        # 遍历所有文件
        for file in files:
            # if file.endswith(".json"):
            if file == file_name:
                file_paths.append(os.path.join(root, file))
    # 返回文件路径列表
    return file_paths


def process_json_files(file_paths):
    # 遍历文件夹下的所有文件和子文件夹
    for file_path in file_paths:
        print("I: processing {}".format(file_path))
        f = open(file_path, encoding='utf8')
        data = json.load(f)
        f.close()
        for k, v in data.items():
            data[k] = sakura_strip(k, v)
        if file_path.endswith("sr.json"):
            with open(file_path, 'w', encoding='utf8') as f3:
                f3.writelines(json.dumps(data, ensure_ascii=False))
        else:
            with open(file_path, 'w', encoding='utf8') as f3:
                f3.writelines(json.dumps(data, ensure_ascii=False, indent=4))


file_paths = read_json_files("D:\\Temp\\230920_MTool_Trans\\sakurallm", 'sp.json')
process_json_files(file_paths)
