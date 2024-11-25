# 导入os和subprocess模块
import os
import subprocess

# 定义一个函数，用于读取指定文件夹下所有.lsb文件（包含子文件夹）
def read_csv_files(folder):
    # 创建一个空列表，用于存储文件路径
    file_paths = []
    # 遍历文件夹下的所有文件和子文件夹
    for root, dirs, files in os.walk(folder):
        # 遍历所有文件
        for file in files:
            # 如果文件是.lsb文件，就将其路径添加到列表中
            if file.endswith("_tr2.csv"):
                file_paths.append(os.path.join(root, file))
    # 返回文件路径列表
    return file_paths

# 定义一个函数，用于对每个文件，在其当前目录执行"lmlsb extractcsv --encoding=utf-8-sig {name}.lsb {name}.csv"，其中"{name}"为文件名（不含扩展名）
def insert_csv(file_paths):
    # 遍历所有文件路径
    for file_path in file_paths:
        # 获取文件名（不含扩展名）
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        # 获取文件所在的目录
        file_dir = os.path.dirname(file_path)
        if "menu" in file_name:
            # 构造命令行参数
            args = ["lmlsb", "insertmenu", "--encoding=utf-8", os.path.join(file_dir, file_name[0:-9] + ".lsb"),
                    file_path]
            # 调用subprocess模块，执行命令
            subprocess.run(args, cwd=file_dir)
        else:
            # 构造命令行参数
            args = ["lmlsb", "insertcsv", "--encoding=utf-8", os.path.join(file_dir, file_name[0:-4] + ".lsb"), file_path]
            # 调用subprocess模块，执行命令
            subprocess.run(args)


# 定义一个指定的文件夹
folder = "D:\\Temp\\230920_MTool_Trans\\livemaker3\\w\\extract"
# 调用read_lsb_files函数，获取文件路径列表
file_paths = read_csv_files(folder)
# 调用extract_csv函数，执行命令
insert_csv(file_paths)
