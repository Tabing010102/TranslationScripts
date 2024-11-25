import json


f = open('r/rr.json', encoding='utf8')
d = json.load(f)

r = {}
for k in sorted(d, key=lambda k: len(d[k]), reverse=True):
    r[k] = d[k]

with open('r/rsp.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(r, ensure_ascii=False, indent=4))
