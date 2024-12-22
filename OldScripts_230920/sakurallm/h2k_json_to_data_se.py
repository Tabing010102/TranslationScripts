import base64
import json

with open('g/name_tr_h2k.json', 'r', encoding='utf8') as f:
    name_tr = json.load(f)
with open('g/msg_tr_h2k.json', 'r', encoding='utf8') as f:
    msg_tr = json.load(f)
with open('g/extension_h2k.json', 'r', encoding='utf8') as f:
    extension = json.load(f)

ENCODING = '932'

data_se = {}
for k, v in name_tr.items():
    data_se[base64.b64encode(k.encode(ENCODING)).decode('ascii')] = base64.b64encode(v.encode(ENCODING)).decode('ascii')
for k, v in msg_tr.items():
    data_se[base64.b64encode(k.encode(ENCODING)).decode('ascii')] = base64.b64encode(v.encode(ENCODING)).decode('ascii')
for k, v in extension.items():
    data_se[base64.b64encode(k.encode(ENCODING)).decode('ascii')] = base64.b64encode(v.encode(ENCODING)).decode('ascii')

with open('g/data_tr_se.json', 'w', encoding='ascii') as f:
    f.writelines(json.dumps(data_se, ensure_ascii=False, indent=4))
