import csv
import json
import os


def read_csv_files(folder):
    # 创建一个空列表，用于存储文件路径
    file_paths = []
    # 遍历文件夹下的所有文件和子文件夹
    for root, dirs, files in os.walk(folder):
        # 遍历所有文件
        for file in files:
            if file.endswith(".csv"):
                file_paths.append(os.path.join(root, file))
    # 返回文件路径列表
    return file_paths


def process_csv_files(file_paths):
    # 遍历文件夹下的所有文件和子文件夹
    for file_path in file_paths:
        f = open(file_path, encoding='utf8')
        # read csv
        reader = csv.reader(f)
        # write
        wfn = file_path.replace("JP", "CN")
        wfndir = os.path.dirname(wfn)
        if not os.path.isdir(wfndir):
            os.makedirs(wfndir)
        writer = csv.writer(open(wfn, 'w', encoding='utf8', newline=""))
        for row in reader:
            try:
                if len(row[2].strip()) == 0:
                    writer.writerow(row)
                    continue
                if row[0] == "ID":
                    writer.writerow(row)
                    continue
                if row[0].startswith("N"):
                    if len(row) != 3:
                        print("W: {} len = {}".format(row[0], len(row)))
                    row.append(get_trans_name(row[2]))
                    writer.writerow(row)
                elif row[0].startswith("L"):
                    if len(row) != 3:
                        print("W: {} len = {}".format(row[0], len(row)))
                    row.append(get_trans_msg(row[2]))
                    writer.writerow(row)
                elif row[0].startswith("S"):
                    if len(row) != 3:
                        print("W: {} len = {}".format(row[0], len(row)))
                    row.append(get_trans_sw(row[2]))
                    writer.writerow(row)
                else:
                    writer.writerow(row)
                    print("W: unknown prefix, row[0] = {}".format(row[0]))
            except Exception as e:
                writer.writerow(row)
                continue


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


def get_trans_sw(s):
    global sw_dict
    if s in sw_dict:
        return sw_dict[s]
    else:
        print("W: untranslated \"sw\": " + s)
        return s


def read_dicts():
    global name_dict
    global msg_dict
    global sw_dict
    f = open('name_tr.json', encoding='utf8')
    name_dict = json.load(f)
    f = open('msg_tr.json', encoding='utf8')
    msg_dict = json.load(f)
    f = open('sw_tr.json', encoding='utf8')
    sw_dict = json.load(f)


# main
name_dict = {}
msg_dict = {}
sw_dict = {}
read_dicts()
file_paths = read_csv_files("D:\\Temp\\ラブラブル～lover able～\\DATA01JP")
process_csv_files(file_paths)
