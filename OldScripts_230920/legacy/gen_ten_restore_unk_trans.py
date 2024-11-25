import json


def need_re_restore(v):
    need_restore = False
    if len(v) == 0:
        need_restore = True
    elif '不知道怎么说' in v:
        need_restore = True
    return need_restore


def restore(o, s):
    r = ''
    if s.strip() == '不知道怎么说':
        r = o
    else:
        r = s.replace('不知道怎么说', '')
        r = r + '///' + o
    return r


result = {}

f2 = open('r/rr.json', encoding='utf8')
ten_data = json.load(f2)

for k, v in ten_data.items():
    if need_re_restore(v):
        result[k] = restore(k, v)
        print('restore: ' + k + ' --> ' + result[k])
    else:
        result[k] = v

with open('r/rr2.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(result, ensure_ascii=False))
with open('r/rp2.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(result, ensure_ascii=False, indent=4))
