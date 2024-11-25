import json

f = open('ManualTransFile.json', encoding='utf8')
ori_data = json.load(f)

f2 = open('r/rr.json', encoding='utf8')
trans_data = json.load(f2)

ret = {}

for k, v in ori_data.items():
    v += '\n'
    v += trans_data[k]
    ret[k] = v

f3 = open('r/rm.json', 'w', encoding='utf8')
f3.writelines(json.dumps(ret, ensure_ascii=False))
