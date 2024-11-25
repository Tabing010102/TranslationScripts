# 导入所需的模块
import os
import openpyxl # 导入openpyxl模块
import json

from utils.is_cjk_str import is_cjk_str


# 定义一个空的字典，用于存储key和value
data = {}

# f = open('ManualTransFile.json', encoding='utf8')
# raw_data = json.load(f)
# raw_data_keys = []
# for key in raw_data:
#     raw_data_keys.append(key)

# 定义一个函数，用于递归读取文件夹中的xlsx文件
def read_xlsx(folder):
    # 遍历文件夹中的所有文件和子文件夹
    for item in os.listdir(folder):
        # 获取文件或子文件夹的完整路径
        path = os.path.join(folder, item)
        # 如果是文件，且扩展名为xlsx
        if os.path.isfile(path) and path.endswith(".xlsx"):
            print("processing " + path)
            # 打开xlsx文件
            workbook = openpyxl.load_workbook(path)
            # 获取第一个工作表
            sheet = workbook.active
            # 遍历工作表中的所有行
            for row in sheet.rows:
                # 获取第一列和第三列的值，作为key和value
                key = row[0].value
                value = row[2].value
                # 将key和value插入字典中
                if is_cjk_str(key):
                    data[key] = value
        # 如果是子文件夹，递归调用函数
        elif os.path.isdir(path):
            read_xlsx(path)

# 调用函数，传入要读取的文件夹路径
read_xlsx("c/i")

# 将字典转换为json格式的字符串
json_data = json.dumps(data, ensure_ascii=False)

# 打开一个json文件，用于写入
with open("c/i/ir.json", "w", encoding='utf8') as f:
    # 将json字符串写入文件中
    f.write(json_data)

# 打开一个json文件，用于写入
with open("c/i/ip.json", "w", encoding='utf8') as f:
    # 将json字符串写入文件中
    f.write(json.dumps(data, ensure_ascii=False, indent=4))

# 打印完成的提示信息
print("Done!")
