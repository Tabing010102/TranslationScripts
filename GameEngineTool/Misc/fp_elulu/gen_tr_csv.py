import csv
import json

from util import *

cn_csv_file_path = f'translation_csv/CHN/trans_scenario.csv'

cn_csv_file = open(cn_csv_file_path, 'r', encoding='utf-16-le')
cn_csv_reader = csv.reader(cn_csv_file, delimiter='\t')
cn_csv_data = list(cn_csv_reader)
cn_csv_file.close()

cn_data = {}
for row in cn_csv_data:
    if is_valid_tr_row(row):
        if row[0] in cn_data:
            print(f"cn Duplicate key: {row[0]}")
        else:
            cn_data[row[0]] = row

jp_csv_file_path = f'translation_csv/JPN/trans_scenario.csv'

jp_csv_file = open(jp_csv_file_path, 'r', encoding='utf-16-le')
jp_csv_reader = csv.reader(jp_csv_file, delimiter='\t')
jp_csv_data = list(jp_csv_reader)
jp_csv_file.close()

tr_data = {}
with open('sp.json', 'r', encoding='utf8') as f:
    tr_data = json.load(f)

# 修改后的代码
with open('tr.csv', 'w', encoding='utf-16-le', newline='') as csv_file:
    tr_csv_writer = csv.writer(csv_file, delimiter='\t')
    for row in jp_csv_data:
        if is_valid_tr_row(row):
            if row[0] in cn_data:
                tr_csv_writer.writerow(cn_data[row[0]])
            elif row[0] in tr_data:
                tr_csv_writer.writerow([row[0], tr_data[row[0]]])
            else:
                tr_csv_writer.writerow(row)
        else:
            tr_csv_writer.writerow(row)
