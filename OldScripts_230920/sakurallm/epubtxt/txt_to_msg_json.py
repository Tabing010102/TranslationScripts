import json

TEXT_SPLIT_LEN = 384
TXT_FILE_NAME = "13.txt"


msgs = {}


if __name__ == "__main__":
    f = open(TXT_FILE_NAME, "r", encoding='utf8')
    lines = f.readlines()
    f.close()

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

    with open('msg.json', 'w', encoding='utf8') as f3:
        f3.writelines(json.dumps(msgs, ensure_ascii=False, indent=4))
