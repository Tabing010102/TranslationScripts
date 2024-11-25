import json

f = open('name_tr.json.bak', encoding='utf8')
name_dict = json.load(f)
f = open('msg_tr.json.bak', encoding='utf8')
msg_dict = json.load(f)
f = open('replace.json', encoding='utf8')
replace_dict = json.load(f)

for nk, nv in name_dict.items():
    for k, v in replace_dict.items():
        if k in nv:
            nv = nv.replace(k, v)
    name_dict[nk] = nv

for nk, nv in msg_dict.items():
    for k, v in replace_dict.items():
        if k in nv:
            nv = nv.replace(k, v)
    msg_dict[nk] = nv

with open('name_tr.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(name_dict, ensure_ascii=False, indent=4))
with open('msg_tr.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(msg_dict, ensure_ascii=False, indent=4))