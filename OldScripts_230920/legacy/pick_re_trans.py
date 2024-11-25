import json


f = open('r/rr.json', encoding='utf8')
d = json.load(f)

r = {}
# for k, v in d.items():
for k in sorted(d, key=lambda k: len(d[k]), reverse=True):
    v = d[k]
    need_re_trans = False
    if len(v) == 0:
        need_re_trans = True
    elif 'sorry' in v or 'Sorry' in v:
        need_re_trans = True
    elif 'apologize' in v or 'Apologize' in v:
        need_re_trans = True
    elif 'ascii' in v or 'ASCII' in v:
        need_re_trans = True
    elif 'japanese' in v or 'Japanese' in v:
        need_re_trans = True
    elif 'simplified' in v or 'Simplified' in v:
        need_re_trans = True
    elif 'chinese' in v or 'Chinese' in v:
        need_re_trans = True
    elif 'can\'t' in v or 'cannot' in v:
        need_re_trans = True
    elif '无法提供' in v or '不能提供' in v:
        need_re_trans = True
    elif '简体中文' in v:
        need_re_trans = True
    elif '似乎没有需要' in v:
        need_re_trans = True
    elif '版权' in v:
        need_re_trans = True

    if need_re_trans:
        r[k] = v


with open('r/re_trans.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(r, ensure_ascii=False, indent=4))
