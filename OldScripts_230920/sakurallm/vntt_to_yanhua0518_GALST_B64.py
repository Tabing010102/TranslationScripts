import base64
import codecs
import json
import os


def read_txt_files(folder):
    # 创建一个空列表，用于存储文件路径
    file_paths = []
    # 遍历文件夹下的所有文件和子文件夹
    for root, dirs, files in os.walk(folder):
        # 遍历所有文件
        for file in files:
            if file.endswith(".txt"):
                file_paths.append(os.path.join(root, file))
    # 返回文件路径列表
    return file_paths


def process_txt_file(txt_file, data_tr, un_trans):
    print(f'I: processing {txt_file}')
    with open(txt_file, 'rb') as f:
        # https://stackoverflow.com/questions/22459020/python-decode-utf-16-file-with-bom
        raw = f.read()
        bom = codecs.BOM_UTF16_LE
        assert raw.startswith(bom)
        raw = raw[len(bom):]
        f2 = raw.decode('utf-16le')
        lines = f2.splitlines()
        f.close()
        # https://stackoverflow.com/questions/71798023/how-to-save-txt-file-with-utf-16-le-bom-encoding-in-python
        f = open(txt_file.replace('txtjp', 'txtcn'), 'wb')
        f.write(bom)
        line1 = ""
        line2 = ""
        c = 0
        i = 0
        while i < len(lines):
            line = lines[i]
            if len(line) == 0:
                f.write('\r\n'.encode('utf-16le'))
                i += 1
                continue
            if c == 0:
                line1 = line
                while not lines[i + 1].startswith('●'):
                    line1 += '\n' + lines[i + 1]
                    i += 1
            elif c == 1:
                line2 = line
                while not len(lines[i + 1]) == 0:
                    line2 += '\n' + lines[i + 1]
                    i += 1
            c += 1
            if c == 2:
                assert len(line1) > 0
                assert len(line2) > 0
                assert line1.startswith('○')
                assert not line1.startswith('●')
                assert line2.startswith('●')
                assert not line2.startswith('○')
                c = 0
                txt = line1[8:]
                txt = txt.replace('〜', '～')
                txt = txt.replace('−', '－')
                if txt not in data_tr:
                    un_trans.append(txt)
                    data_tr[txt] = base64.b64encode(txt.encode('932')).decode('932')
                    print(f"W: untranslated txt: {txt} -> {data_tr[txt]}")
                f.write((line1.replace('\n', '\r\n') + '\r\n').encode('utf-16le'))
                f.write((line2[:8] + data_tr[txt].replace('\n', '\r\n') + '\r\n').encode('utf-16le'))
                line1 = ""
                line2 = ""
            i += 1
        f.close()


if __name__ == "__main__":
    #### original
    # f = open('D:\\Temp\\ラブピカルポッピー！\\msg_tr.json', encoding='utf8')
    # msg_tr = json.load(f)
    # f = open('D:\\Temp\\ラブピカルポッピー！\\name_tr.json', encoding='utf8')
    # name_tr = json.load(f)
    # data_tr = msg_tr
    # for k, v in name_tr.items():
    #     data_tr[k] = v
    #### sjistunnel
    f = open('g/data_tr_se.json')
    data_tr_ori = json.load(f)
    data_tr = {}
    for k, v in data_tr_ori.items():
        data_tr[base64.b64decode(k).decode('932')] = data_tr_ori[k]
    txt_files = read_txt_files("g/txtjp")
    un_trans = []
    for txt_file in txt_files:
        process_txt_file(txt_file, data_tr, un_trans)
    with open(f'g/un_trans.txt', 'w', encoding='utf8') as f:
        f.writelines('\n'.join(un_trans))
