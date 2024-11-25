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


# 定义一个函数，接受一个字符串作为参数
def has_japanese(string):
    # 导入正则表达式模块
    import re
    # 定义一个正则表达式，匹配日文字符的范围
    regex = r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff66-\uff9f]"
    # 使用search方法，查找字符串中是否有匹配的字符
    match = re.search(regex, string)
    # 如果有匹配，返回True，否则返回False
    return bool(match)
