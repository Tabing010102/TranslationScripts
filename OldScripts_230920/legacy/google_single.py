import json
import time

from googletrans import Translator

from deep_translator import GoogleTranslator


# https://stackoverflow.com/questions/30069846/how-to-find-out-chinese-or-japanese-character-in-a-string-in-python
def is_cjk(character):
    """
    Checks whether character is CJK.

        >>> is_cjk(u'\u33fe')
        True
        >>> is_cjk(u'\uFE5F')
        False

    :param character: The character that needs to be checked.
    :type character: char
    :return: bool
    """
    return any([start <= ord(character) <= end for start, end in
                [(4352, 4607), (11904, 42191), (43072, 43135), (44032, 55215),
                 (63744, 64255), (65072, 65103), (65381, 65500),
                 (131072, 196607)]
                ])


def is_cjk_str(s):
    for c in s:
        if is_cjk(c):
            return True
    return False


f = open('ManualTransFile.json', encoding='utf8')
raw_data = json.load(f)
i = 0
raw_data_subscript_dict = {}
for key in raw_data:
    raw_data_subscript_dict[i] = key
    i = i + 1


i = 0
dlen = len(raw_data)


MAX_LEN = 5000

req_i = 0

raw_data_replace_dict = {}

translator = Translator(raise_exception=True)

while True:

    try:
        src_list = []
        req_to_global_seqn_dict = {}
        cnt_len = 0
        j = 0
        while True:
            while i < dlen and is_cjk_str(raw_data[raw_data_subscript_dict[i]]) == False:
                i = i + 1
            if i >= dlen:
                break
            cnt_s_len = len(raw_data[raw_data_subscript_dict[i]])
            if cnt_len + cnt_s_len > MAX_LEN or i >= dlen:
                break
            cnt_len += cnt_s_len
            src_list.append(raw_data[raw_data_subscript_dict[i]])
            req_to_global_seqn_dict[j] = i
            i = i + 1
            j = j + 1


        resp = {}
        while True:
            try:
                # resp = translator.translate(src_list, src='ja', dest='zh-cn')
                resp = GoogleTranslator(source='ja', target='zh-cn').translate_batch(src_list)
                break
            except Exception as err:
                print(err)
                print('retrying')
                continue


        ret = {}

        # text_list = []
        text_list = resp.values()

        for j in range(len(text_list)):
            ret[j] = text_list[j]
            raw_data[raw_data_subscript_dict[req_to_global_seqn_dict[j]]] = text_list[j]
            # raw_data_replace_dict[req_to_global_seqn_dict[j]] = text_list[j]

        f2_name = 'g/' + str(req_i) + '_raw.txt'
        with open(f2_name, 'w', encoding='utf8') as f2:
            f2.writelines(resp.to_json_string())

        f2_name = 'g/' + str(req_i) + '_seqn.txt'
        with open(f2_name, 'w', encoding='utf8') as f2:
            f2.writelines(json.dumps(req_to_global_seqn_dict))

        print(str(req_i) + ', g_p = ' + str(i) + '')

        req_i = req_i + 1

        # break

        if i >= dlen:
            break

        # time.sleep(100)

    except Exception as err:
        print(err)


with open('g/gr.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(raw_data, ensure_ascii=False))
with open('g/gp.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(raw_data, ensure_ascii=False, indent=4))


