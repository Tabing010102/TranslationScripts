def get_replace_dict(file_path='hanzi2kanji_table.txt'):
    f = open(file_path, 'r', encoding='utf8')
    ret = {}
    for line in f.readlines():
        line = line.strip()
        if len(line) == 0:
            continue
        line = line.split('\t')
        ret[line[0]] = line[1]
        assert len(line[0]) == 1
        assert len(line[1]) == 1
    f.close()
    return ret


def h2k_rep_p1(s, ud, replace_dict):
    for c in s:
        if c in replace_dict:
            ud[c] = replace_dict[c]


def h2k_rep_p2(s, ud, none_932_char):
    for c in s:
        try:
            c.encode('932')
        except:
            if c not in ud:
                none_932_char.append(c)


def process_with_unused_replace_char(none_932_char, used_replace_dict, replace_dict):
    unused_replace_char = []
    for k in replace_dict.keys():
        if k not in used_replace_dict:
            unused_replace_char.append(k)
    if len(none_932_char) > len(unused_replace_char):
        raise Exception('no more char')
    for i in range(len(none_932_char)):
        used_replace_dict[none_932_char[i]] = replace_dict[unused_replace_char[i]]


def get_h2k_str(s, ud):
    ret = ""
    for c in s:
        if c in ud:
            ret += ud[c]
        else:
            ret += c
    ret.encode('932')
    return ret


if __name__ == '__main__':
    replace_dict = get_replace_dict()
    infile_path = 'g/msg_tr.json'
    outfile_path = 'g/msg_tr_h2k.json'
    h2k_file_path = 'g/h2k.txt'
    used_replace_dict = {}

    fin = open(infile_path, 'r', encoding='utf8')
    lines = fin.readlines()
    fin.close()
    for line in lines:
        h2k_rep_p1(line, used_replace_dict, replace_dict)
    none_932_char = []
    for line in lines:
        h2k_rep_p2(line, used_replace_dict, none_932_char)
    process_with_unused_replace_char(none_932_char, used_replace_dict, replace_dict)
    fout = open(outfile_path, 'w', encoding='utf8')
    for line in lines:
        fout.write(get_h2k_str(line, used_replace_dict))
    fout.close()


    infile_path = 'g/name_tr.json'
    outfile_path = 'g/name_tr_h2k.json'
    fin = open(infile_path, 'r', encoding='utf8')
    lines = fin.readlines()
    fin.close()
    for line in lines:
        h2k_rep_p1(line, used_replace_dict, replace_dict)
    for line in lines:
        h2k_rep_p2(line, used_replace_dict, none_932_char)
    process_with_unused_replace_char(none_932_char, used_replace_dict, replace_dict)
    fout = open(outfile_path, 'w', encoding='utf8')
    for line in lines:
        fout.write(get_h2k_str(line, used_replace_dict))
    fout.close()


    infile_path = 'g/extension.json'
    outfile_path = 'g/extension_h2k.json'
    fin = open(infile_path, 'r', encoding='utf8')
    lines = fin.readlines()
    fin.close()
    for line in lines:
        h2k_rep_p1(line, used_replace_dict, replace_dict)
    for line in lines:
        h2k_rep_p2(line, used_replace_dict, none_932_char)
    process_with_unused_replace_char(none_932_char, used_replace_dict, replace_dict)
    fout = open(outfile_path, 'w', encoding='utf8')
    for line in lines:
        fout.write(get_h2k_str(line, used_replace_dict))
    fout.close()


    f = open(h2k_file_path, 'w', encoding='utf8')
    ori_s = ""
    rep_s = ""
    for k, v in used_replace_dict.items():
        ori_s += k
        rep_s += v
    f.write(ori_s)
    f.write('\n')
    f.write(rep_s)
    f.close()
