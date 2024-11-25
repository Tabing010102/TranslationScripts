# 导入os和json模块
import os
import json

import utils


# 定义一个函数，用于读取指定文件夹下所有.txt文件（包含子文件夹）
def read_txt_files(folder):
    # 创建一个空列表，用于存储文件路径
    file_paths = []
    # 遍历文件夹下的所有文件和子文件夹
    for root, dirs, files in os.walk(folder):
        # 遍历所有文件
        for file in files:
            # 如果文件是.txt文件，就将其路径添加到列表中
            if file.endswith(".txt"):
                file_paths.append(os.path.join(root, file))
    # 返回文件路径列表
    return file_paths

# 定义一个函数，用于忽略文件每一行中的"<num,num,num>"，其中"num"代表任意数字
def ignore_num(line):
    # 导入re模块，用于正则表达式匹配
    import re
    # 定义一个正则表达式，用于匹配"<num,num,num>"的模式
    pattern = r"<\d+,\d+,\d+>"
    # 使用re.sub函数，将匹配到的模式替换为空字符串
    line = re.sub(pattern, "", line)
    # 返回处理后的行
    return line

# 定义一个函数，用于忽略以"D:\"、"_"开头的行
def ignore_start(line):
    # 如果行以"D:\"或"_"开头，就返回False，表示忽略该行
    if line.startswith("D:\\") or line.startswith("_"):
        return False
    # 否则，返回True，表示保留该行
    else:
        return True

# 定义一个函数，用于以json格式输出一个dict，key和value都为忽略开头的"<num,num,num>"后该行余下的字符串
def output_json(file_paths):
    # 创建一个空字典，用于存储结果
    result = {}
    # 遍历所有文件路径
    for file_path in file_paths:
        # 打开文件，以只读模式
        with open(file_path, "r", encoding="utf8") as f:
            # 遍历文件的每一行
            for line in f:
                # 去掉行尾的换行符
                line = line.strip()
                # 忽略文件每一行中的"<num,num,num>"
                line = ignore_num(line)
                # 如果行不为空，且不以"D:\"、"_"开头
                if line and ignore_start(line) and utils.is_cjk_str(line):
                    # 将行作为key和value，添加到字典中
                    result[line] = line
    # 将字典转换为json格式的字符串
    json_str = json.dumps(result, ensure_ascii=False, indent=4)
    # 返回json字符串
    return json_str

# 定义一个指定的文件夹
folder = "D:\\Temp\\230920_MTool_Trans\\sakurallm\\g"
# 调用read_txt_files函数，获取文件路径列表
file_paths = read_txt_files(folder)
# 调用output_json函数，获取json字符串
json_str = output_json(file_paths)
# 打印json字符串
# print(json_str)
with open('ManualTransFile.json', 'w', encoding='utf8') as f3:
    f3.write(json_str)
