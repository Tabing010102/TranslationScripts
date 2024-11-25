import json

if __name__ == "__main__":
    f = open('msg_tr.json', encoding='utf8')
    ori_data = json.load(f)
    for k, v in ori_data.items():
        # replace \r\n with \n
        k = k.replace("\r\n", "\n")
        v = v.replace("\r\n", "\n")
        data[k] = v

    with open('msg.json', 'w', encoding='utf8') as f3:
        f3.writelines(json.dumps(data, ensure_ascii=False, indent=4))
