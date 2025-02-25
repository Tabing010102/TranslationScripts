import csv
import json

csv_file_path = f'translation_csv/CHN/trans_name.csv'

csv_file = open(csv_file_path, 'r', encoding='utf-16-le')
csv_reader = csv.reader(csv_file, delimiter='\t')
csv_data = list(csv_reader)
csv_file.close()

dict_data = {}
for row in csv_data:
    if row[0] and row[1]:
        dict_data[row[0]] = row[1]

with open('dict.json', 'w', encoding='utf8') as f:
    json.dump(dict_data, f, ensure_ascii=False, indent=4)
