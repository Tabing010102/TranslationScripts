import json


def get_trans_name(s: str):
    global name_dict
    if name_dict.__contains__(s):
        return name_dict[s]
    else:
        print("W: name not found: " + s)
        return s


def get_replaced_content(s: str):
    r = ""
    if s.__contains__('＠'):
        names = s.split('＠')
        first = True
        for name in names:
            if first:
                first = False
            else:
                r += '＠'
            r += get_trans_name(name)
    else:
        r = get_trans_name(s)
    return r


f = open('name_tr.json', encoding='utf8')
name_dict = json.load(f)

file_path = 'キャラ名定義.txt.ybn.txt'

f = open(file_path, encoding="utf-8-sig")
f2 = open(file_path + '.new', "w", encoding="utf-8-sig")
for line in f.readlines():
    if line[-1] == "\n":
        line = line[:-1]
    line = line[1:-1]
    if line[0] == '【':
        f2.write("\"【" + get_replaced_content(line[1:-1]) + "】\"\n")
    else:
        f2.write("\"" + get_replaced_content(line) + "\"\n")
f2.close()
