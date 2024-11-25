import json

f = open('ManualTransFile.json', encoding='utf8')
ori_data = json.load(f)

f2 = open('r/rr.json', encoding='utf8')
trans_data = json.load(f2)

ret = {}

i = 0
for k, v in ori_data.items():
    if trans_data.get(i) is not None and len(trans_data[i]) > 0:
        v = trans_data[i]
    ret[k] = v
    i = i + 1

f3 = open('r/rm.json', 'w', encoding='utf8')
f3.writelines(json.dumps(ret, ensure_ascii=False))
