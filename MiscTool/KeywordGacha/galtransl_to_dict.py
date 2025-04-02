import json
import os

DIR = '/path/to/kg_output'

# read all _galtransl.txt
files = [f for f in os.listdir(DIR) if f.endswith('_galtransl.txt')]
# get full path
files = [os.path.join(DIR, f) for f in files]

dict_raw = {}

for f in files:
    with open(f, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for l in lines:
            words = l.split('\t')
            words = [w.strip() for w in words]
            if len(words) < 2 or len(words) > 3:
                print(f'W: Skipping line: {l}')
                continue
            if words[0] in dict_raw:
                print(f'W: Duplicate key: {words[0]}')
                continue
            dict_raw[words[0]] = [words[1]]
            if len(words) == 3:
                dict_raw[words[0]].append(words[2])

with open('dict.json', 'w', encoding='utf8') as f:
    json.dump(dict_raw, f, ensure_ascii=False, indent=4)
