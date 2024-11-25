import json


result = {}

f = open('ManualTransFile.json', encoding='utf8')
ori_data = json.load(f)
f2 = open('r/rp_m.json', encoding='utf8')
trans_data = json.load(f2)
f3 = open('r/re_trans_m.json', encoding='utf8')
re_trans_data = json.load(f3)


i = 0
for k, v in ori_data.items():
    if re_trans_data.get(k) is not None:
        result[k] = re_trans_data[k].replace('\n\n', '\n').strip()
    else:
        if trans_data.get(str(i)) is None:
            result[k] = v
        else:
            result[k] = trans_data[str(i)]

    i = i + 1

with open('r/rr2.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(result, ensure_ascii=False))
with open('r/rp2.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(result, ensure_ascii=False, indent=4))
