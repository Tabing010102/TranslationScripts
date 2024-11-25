import json


result = {}

f = open('ManualTransFile.json', encoding='utf8')
ori_data = json.load(f)
f2 = open('r/re_trans.json', encoding='utf8')
re_trans_data = json.load(f2)

m = {}

i = 0
for k, v in ori_data.items():
    m[i] = v
    i = i + 1

for k, v in re_trans_data.items():
    result[m[int(k)]] = v

with open('r/re_trans_m_gen.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(result, ensure_ascii=False, indent=4))
