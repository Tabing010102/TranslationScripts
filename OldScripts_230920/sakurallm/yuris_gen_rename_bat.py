f = open('pac_name.txt', encoding='utf8')

for line in f.readlines():
    bs1 = line.encode("932")
    bs2 = line.encode("936")
    if bs1 != bs2:
        print(line)




fa = open('apply.bat', encoding='utf8')
fr = open('restore.bat', encoding='utf8')