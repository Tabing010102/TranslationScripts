import json
import os

WORKING_DIR = 'w'
IN_FILE = 'result.txt'
IN_ENCODING = '932'
OUT_FILE = 'ManualTransFile.json'


def read_decompiled(file_path, encoding) -> dict[str, str]:
    with open(file_path, 'r', encoding=encoding) as f:
        lines = f.readlines()
    result = {}
    for line in lines:
        # strip text after ;
        line = line.split(';')[0].strip()
        if len(line) >= 2 and line[-1] == '\\':
            result[line[:-1]] = line[:-1]
    return result


def get_trans_dirs(working_dir):
    matching_dirs = []
    for root, dirs, files in os.walk(working_dir):
        if IN_FILE in files:
            if OUT_FILE in files:
                print(f'{root} has been imported, skipping')
            else:
                matching_dirs.append(root)
    return matching_dirs


if __name__ == '__main__':
    for dir in get_trans_dirs(WORKING_DIR):
        print(f'Processing {dir}')
        data = read_decompiled(IN_FILE, encoding=IN_ENCODING)
        with open(os.path.join(dir, OUT_FILE), 'w', encoding='utf8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
