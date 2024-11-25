import json

f = open('msg_tr.json', encoding='utf8')
data = json.load(f)

for k, v in data.items():
    if len(k) <= 2:
        continue
    if k[-1] == '」' and k[-2] != '。' and v[-2] == '。' and k[-2] != '？' and k[-2] != '！':
        data[k] = v[:-2] + v[-1]
    elif k[-1] != '」' and k[-1] != '。' and v[-1] == '。' and k[-1] != '？' and k[-1] != '！':
        data[k] = v[:-1]

with open('msg_tr_s.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(data, ensure_ascii=False, indent=4))
