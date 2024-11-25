# 导入os、csv和codecs模块
import json
import os
import csv
import codecs

import utils
from sakurallm.sakura import translate_ensured


# 定义一个函数，用于读取指定文件夹下所有.csv文件（包含子文件夹）
def read_csv_files(folder):
    # 创建一个空列表，用于存储文件路径
    file_paths = []
    # 遍历文件夹下的所有文件和子文件夹
    for root, dirs, files in os.walk(folder):
        # 遍历所有文件
        for file in files:
            # 如果文件是.csv文件，就将其路径添加到列表中
            if file.endswith(".csv"):
                file_paths.append(os.path.join(root, file))
    # 返回文件路径列表
    return file_paths


# # 定义一个函数，用于调用"translate(cur_ori_text)"，返回结果为str，赋值给cur_trans_text
# def translate(cur_ori_text):
#     # 这里假设你已经定义了一个translate函数，用于实现文本翻译的功能
#     # 如果没有，你可以使用Bing翻译API或其他第三方库来实现
#     # 请参考https://docs.microsoft.com/zh-cn/azure/cognitive-services/translator/translator-how-to-signup
#     # 这里只是简单地返回原文本作为示例
#     cur_trans_text = cur_ori_text
#     # 返回翻译后的文本
#     return cur_trans_text


trans_json_raw = {}
# 定义一个函数，用于将每一行中的第4个字段作为cur_ori_text变量，将cur_trans_text填入csv同一行中的第5个字段，将新生成的csv文件以utf8编码保存为"{csv_file_name}_new.csv"
def process_csv(file_paths):
    global trans_json_raw
    # 遍历所有文件路径
    for file_path in file_paths:
        print("processing " + file_path)
        # 获取文件名（不含扩展名）
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        # 获取文件所在的目录
        file_dir = os.path.dirname(file_path)
        # 以utf8编码打开原始csv文件，以只读模式
        with codecs.open(file_path, "r", encoding="utf-8") as f_in:
            # 创建一个csv阅读器，用于读取每一行
            reader = csv.reader(f_in)
            for row in reader:
                if row:
                    trans_json_raw[row[3]] = row[3]


# 定义一个指定的文件夹
folder = ".\\w"
# 调用read_csv_files函数，获取文件路径列表
file_paths = read_csv_files(folder)
# 调用process_csv函数，处理csv文件
process_csv(file_paths)

with open('.\\w\\msg.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(trans_json_raw, ensure_ascii=False, indent=4))
