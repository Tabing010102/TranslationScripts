# 打开1.txt文件并读取内容
with open("adv32_hex.txt", "r") as f:
    hex_str = f.read()

# 创建一个空字符串用于存储运算后的结果
result = ""

# 遍历每两个字符
for i in range(0, len(hex_str), 2):
    # 将两个字符转换为16进制数
    hex_num = int(hex_str[i:i+2], 16)
    # 与0x40做位运算
    hex_num = hex_num + 0x40
    # 将运算后的16进制数转换为字符串并拼接到结果字符串
    result += hex(hex_num)[2:]

# 打开2.txt文件并写入结果
with open("adv32_hex_c.txt", "w") as f:
    f.write(result)
