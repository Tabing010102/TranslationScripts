import json
import re
import time
from urllib.parse import urlencode

import requests

# DEL_DUP_LN = [0, 999999]

# RJ237448 行け!! 鳴神学園オカルト研究部2
# DEL_DUP_LN = [0, 2637, 19658, 21311, 36491, 99999999]
# RJ01042745 見習いモビィと風待ちの島 ver1.2.7
# DEL_DUP_LN = [0, 6009, 26846, 999999, 11014, 11397, 20685, 24209]
# RJ352933 リコの不思議なお使い_製品版_Ver1.40
# DEL_DUP_LN = [0, 5195, 7283, 8621, 11152, 13749, 15050, 15183, 15685, 9999999]
# RJ01116296 プリンセスシャーロット【前編】 ～ぼくとお姫さまの秘密の旅～
# DEL_DUP_LN = [0, 2003, 9125, 11200, 13233, 9999999]
# RJ406267 シェリル～金色の竜と遺跡の島～_Ver1.91+Append_Ver1.0
# DEL_DUP_LN = [0, 1602, 1604, 1634, 1636, 1649, 1651, 1661, 1663, 1732, 1734, 1771,
#               1777, 1903, 1905, 1922, 1924, 1929, 1966, 2021, 2023, 2064,
#               2066, 2097, 2099, 2128, 2130, 2149, 2177, 2234, 2235, 2425,
#               2427, 2658, 2660, 3285, 3287, 3305, 3309, 3884, 3990, 4322,
#               4326, 4406, 4450, 4481, 4488, 4839, 4841, 4868, 4891, 4916,
#               4918, 5116, 5120, 5131, 5133, 5272, 5273, 5446, 5462, 5634,
#               5636, 5655, 5657, 5711, 5713, 5739, 5741, 5789, 5794, 5794,
#               5800, 5954, 5956, 6308, 6323, 6323, 6336, 6359, 6363, 6444,
#               6457, 6457, 6482, 6586, 6589, 6589, 6621, 6621, 6642, 6643,
#               6648, 6652, 6661, 6661, 6666, 6666, 6668, 6688, 6745, 6758,
#               6766, 6776, 6789, 6789, 6791, 6791, 6794, 6794, 6806, 6815,
#               6834, 7081, 7100, 7143, 7171, 7177, 7185, 7196, 7202, 7202,
#               7215, 7215, 7239, 7245, 7255, 7338, 7346, 7402, 7436, 7858,
#               7985, 8003, 16503, 16506, 16559, 16559, 16583, 16602, 16665, 16665,
#               16754, 16760, 17773, 17795, 17808, 17828, 17844, 17844, 17857, 17857,
#               17920, 17920, 19541, 19543, 19703, 19735, 19756, 19785, 19818, 19818,
#               21137, 21346, 21455, 22991, 23007, 999999]
# UNDEL_DUP_LN = [1627, 1983, 2235, 2611, 2660, 5273, 6806, 7346]
# RJ01122385 スラム街案内人
# DEL_DUP_LN = [0, 1342, 1352, 1352, 1431, 1596, 1853, 1853, 1886, 1996, 2091, 2091, 2108, 2140, 2196, 2196,
#               2211, 2211, 2459, 2459, 2560, 2716, 7872, 7873, 8896, 9713]
# UNDEL_DUP_LN = [1966, 1974, 1989, 8906, 9004, 9036, 916, 936, 962, 988, 990, 997, 1022, 1058, 1067, 1214,
#                 1249, 1263, 1277, 1295, 1299, 1303, 1305, 1329, 1334, 1342, 1451, 1482, 1499, 1518, 1538,
#                 1563, 1581, 1587, 1591, 2484, 2566, 2575, 2625, 2630, 2649, 2655]
# RJ01099962 [秘密結社ロリコーン 開発部]リリィちゃんと不思議でえっちなダンジョン v1.00
DEL_DUP_LN = [0, 1200, 1454, 1476, 1487, 1491, 1499, 1499, 1674, 1674, 1696, 1775,
              4669, 5052, 5267, 5821, 7220, 999999]
UNDEL_DUP_LN = [813, 814, 851, 949, 1699, 1708, 1747, 4782, 4982, 4992, 5554, 5692,
                5758, 5773, 7228, 7250, 7255, 7271, 7282, 8323, 12121, 12178,
                1781]


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


def need_re_del(k, v, i):
    if not is_cjk_str(k):
        return 0
    need_del = 0
    if ('(' not in k and '（' not in k and '【' not in k and '）' not in k) and ('(' in v or '（' in v):
        need_del = 1
    elif in_range(i) and ('；' not in k and '：' not in k and '，' not in k and '、' not in k and ',' not in k) \
            and ('；' in v or '：' in v or '，' in v):
        need_del = 2
    elif in_range(i) and is_concatenated_chinese(v):
        need_del = 3
    return need_del


def in_range(ln):
    i = 0
    while i < len(DEL_DUP_LN):
        st = DEL_DUP_LN[i]
        sp = DEL_DUP_LN[i+1]
        if ln >= st and ln <= sp:
            if (ln not in UNDEL_DUP_LN):
                return True

        i = i + 2
    return False

def do_del(o, s, need_del):
    r = ''
    if need_del == 1:
        a = r'\(.*?\)'
        r = re.sub(a, '', s)
    elif need_del == 2:
        r = remove_until_first_occurrence(s)
    elif need_del == 3:
        half_length = len(s) // 2
        r = s[:half_length]
    return r


def remove_until_first_occurrence(s):
    MAXV = 999999
    fo = MAXV
    if s.find('；') != -1:
        fo = min(fo, s.find('；'))
    if s.find('：') != -1:
        fo = min(fo, s.find('：'))
    if s.find('，') != -1:
        fo = min(fo, s.find('，'))
    if fo == MAXV:
        fo = -1
    first_occurrence = fo
    if first_occurrence == -1:
        return s
    else:
        return s[:first_occurrence]


def remove_punctuation(input_string):
    # 使用正则表达式去除标点符号
    cleaned_string = re.sub(r'[^\w\s]', '', input_string)
    return cleaned_string


def is_concatenated_chinese(s):
    cleaned_s = remove_punctuation(s)
    length = len(cleaned_s)

    if length % 2 != 0:
        return False

    half_length = length // 2
    first_half = cleaned_s[:half_length]
    second_half = cleaned_s[half_length:]

    return first_half == second_half

result = {}

f2 = open('r/rr2.json', encoding='utf8')
ten_data = json.load(f2)

i = 2
for k, v in ten_data.items():
    need_del = need_re_del(k, v, i)
    if need_del != 0:
        result[k] = do_del(k, v, need_del)
        print('del(' + str(i) + '): ' + k + ' --> ' + result[k])
    else:
        result[k] = v
    i = i + 1

with open('r/rr3.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(result, ensure_ascii=False))
with open('r/rp3.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(result, ensure_ascii=False, indent=4))
