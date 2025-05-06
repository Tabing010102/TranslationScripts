import json
import os

DIR = '/path/to/kg_output'

# read all .json
files = [f for f in os.listdir(DIR) if f.endswith('.json')]
# get full path
files = [os.path.join(DIR, f) for f in files]

dict_raw = {}

for f in files:
    fjson = json.load(open(f, 'r', encoding='utf-8'))
    for entry in fjson:
        dict_raw[entry['src']] = [entry['dst']]
        if 'info' in entry:
            dict_raw[entry['src']].append(entry['info'])

with open('dict.json', 'w', encoding='utf8') as f:
    json.dump(dict_raw, f, ensure_ascii=False, indent=4)
