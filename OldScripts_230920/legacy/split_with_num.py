import json


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
result = {}
for k, v in raw_data.items():
    if is_cjk_str(k):
        result[i] = k
    i = i + 1

with open('ManualTransFile_FN.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(result, ensure_ascii=False, indent=4))
