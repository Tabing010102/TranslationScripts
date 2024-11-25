import json


TEXT_SPLIT_LEN = 384
TXT_FILE_NAME = "13.txt"


if __name__ == "__main__":
    f = open('msg_tr.json', encoding='utf8')
    msg_tr = json.load(f)
    f.close()

    f = open(TXT_FILE_NAME, "r", encoding='utf8')
    lines = f.readlines()
    f.close()

    msgs = {}
    # split to TEXT_SPLIT_LEN
    cnt_len = 0
    cnt_msg = ""
    for line in lines:
        if cnt_len + len(line) <= TEXT_SPLIT_LEN:
            if len(line.strip()) == 0:
                continue
            cnt_msg += line
            cnt_len += len(line)
        else:
            cnt_msg = cnt_msg.strip()
            msgs[cnt_msg] = cnt_msg
            cnt_len = len(line)
            cnt_msg = line
    if len(cnt_msg) > 0:
        cnt_msg = cnt_msg.strip()
        msgs[cnt_msg] = cnt_msg

    f = open('r.txt', 'w', encoding='utf8')
    for k, v in msgs.items():
        if k not in msg_tr:
            print(f"W: {k} not found")
        else:
            f.write(f"{msg_tr[k]}\n")
    f.close()
