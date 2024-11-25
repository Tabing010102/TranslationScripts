import json

if __name__ == "__main__":
    f = open('msgp.json', encoding='utf8')
    msgp = json.load(f)

    msgp_map = {}

    for k, v in msgp.items():
        # replace \r\n with \n
        k2 = k.replace("\r\n", "\n")
        msgp_map[k2] = k

    data = {}

    f = open('msg_tr.json', encoding='utf8')
    msg_tr = json.load(f)

    for k, v in msg_tr.items():
        ori_k = msgp_map[k]
        v2 = v.replace("\n", "\r\n")
        data[ori_k] = v2

    with open('msg_tr2.json', 'w', encoding='utf8') as f3:
        f3.writelines(json.dumps(data, ensure_ascii=False, indent=4))
