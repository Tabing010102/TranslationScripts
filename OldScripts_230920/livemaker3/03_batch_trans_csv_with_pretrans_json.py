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

# 定义一个函数，用于将每一行中的第4个字段作为cur_ori_text变量，将cur_trans_text填入csv同一行中的第5个字段，将新生成的csv文件以utf8编码保存为"{csv_file_name}_new.csv"
def process_csv(file_paths):
    # 遍历所有文件路径
    for file_path in file_paths:
        # 获取文件名（不含扩展名）
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        # 获取文件所在的目录
        file_dir = os.path.dirname(file_path)
        # 以utf8编码打开原始csv文件，以只读模式
        with codecs.open(file_path, "r", encoding="utf-8") as f_in:
            # 创建一个csv阅读器，用于读取每一行
            reader = csv.reader(f_in)
            row_count = sum(1 for row in reader)
        with codecs.open(file_path, "r", encoding="utf-8") as f_in:
            # 创建一个csv阅读器，用于读取每一行
            reader = csv.reader(f_in)
            # 以utf8编码打开新的csv文件，以写入模式
            with codecs.open(os.path.join(file_dir, file_name + "_tr.csv"), "w", encoding="utf-8") as f_out:
                # 创建一个csv写入器，用于写入每一行
                writer = csv.writer(f_out)
                line_count = 0
                # 遍历每一行
                for row in reader:
                    line_count = line_count + 1
                    if line_count == 1:
                        writer.writerow(row)
                        print("[" + os.path.basename(file_path) + "] skipping L1")
                        continue
                    # 如果行不为空
                    if row:
                        # 将每一行中的第4个字段作为cur_ori_text变量
                        cur_ori_text = row[3]
                        if utils.is_cjk_str(cur_ori_text):
                            # 调用translate函数，获取翻译后的文本
                            cur_trans_text = translate_from_json(cur_ori_text)
                            # 将cur_trans_text填入csv同一行中的第5个字段
                            row[4] = cur_trans_text
                            # 将新的行写入新的csv文件
                            writer.writerow(row)
                            print("[" + os.path.basename(file_path) + "] L[" + str(line_count) + "/" +
                                  str(row_count) + "]: " + cur_ori_text + " -> " + cur_trans_text)
                        else:
                            row[4] = cur_ori_text
                            writer.writerow(row)
                            print("[" + os.path.basename(file_path) + "] L[" + str(line_count) + "/" +
                                  str(row_count) + "]: " + cur_ori_text + " -> skipped")


def translate_from_json(s):
    if s in trans_json_dict:
        return trans_json_dict[s]
    else:
        return s


f = open('.\\w\\msg_tr.json', encoding='utf8')
folder = ".\\w\\extract"
trans_json_dict = json.load(f)
# 定义一个指定的文件夹
# 调用read_csv_files函数，获取文件路径列表
file_paths = read_csv_files(folder)
# 调用process_csv函数，处理csv文件
process_csv(file_paths)
