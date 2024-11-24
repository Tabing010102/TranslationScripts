def sakura_strip(k: str, v: str) -> str:
    if len(k) < 2 or len(v) < 2:
        return v
    if k[0] != '「' and v[0] == '「':
        v = v[1:]
    if k[-1] != '」' and v[-1] == '」':
        v = v[:-1]
    if len(v) < 2:
        return v
    if k[-1] == '」' and k[-2] != '。' and k[-2] != '？' and k[-2] != '！' and v[-2] == '。':
        v = v[:-2] + v[-1]
    if k[-1] != '」' and k[-1] != '。' and k[-1] != '？' and k[-1] != '！' and v[-1] == '。':
        v = v[:-1]
    return v
