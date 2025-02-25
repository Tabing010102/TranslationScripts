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
            cn_data[row[0]] = row[1]


jp_csv_file_path = f'translation_csv/JPN/trans_scenario.csv'

jp_csv_file = open(jp_csv_file_path, 'r', encoding='utf-16-le')
jp_csv_reader = csv.reader(jp_csv_file, delimiter='\t')
jp_csv_data = list(jp_csv_reader)
jp_csv_file.close()

jp_in_cn_count = 0
jp_dup_count = 0
mtool_data = {}
for row in jp_csv_data:
    if is_valid_tr_row(row):
        if row[0] in cn_data:
            jp_in_cn_count += 1
        elif row[0] in mtool_data:
            print(f"jp Duplicate key: {row[0]}")
            jp_dup_count += 1
        else:
            mtool_data[row[0]] = row[0]

with open('ManualTransFile.json', 'w', encoding='utf8') as f:
    json.dump(mtool_data, f, ensure_ascii=False, indent=4)
