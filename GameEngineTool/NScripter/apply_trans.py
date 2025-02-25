import json
import os

WORKING_DIR = 'w'
IN_FILE = 'sp.json'
SCRIPT_FILE = 'result.txt'
SCRIPT_ENCODING = '932'
OUT_FILE = '0.utf.txt'


def apply_trans(script_dir_path, tr_data: dict[str, str]):
    script_file_path = os.path.join(script_dir_path, SCRIPT_FILE)
    with open(script_file_path, 'r', encoding=SCRIPT_ENCODING) as f:
        lines = f.readlines()
    result = []
    for ori_line in lines:
        # strip text after ;
        line = ori_line.split(';')[0].strip()
        if len(line) >= 2 and line[-1] == '\\':
            result.append(tr_data.get(line[:-1], line[:-1]) + '\\')
        else:
            result.append(ori_line)
    with open(os.path.join(script_dir_path, OUT_FILE), 'w', encoding='utf8') as f:
        f.writelines(result)


def get_trans_dirs(working_dir):
    matching_dirs = []
    for root, dirs, files in os.walk(working_dir):
        if IN_FILE in files:
            if OUT_FILE in files:
                print(f'{root} has been translated, skipping')
            else:
                matching_dirs.append(root)
    return matching_dirs


if __name__ == '__main__':
    for dir in get_trans_dirs(WORKING_DIR):
        print(f'Processing {dir}')
        with open(os.path.join(dir, IN_FILE), 'r', encoding='utf8') as f:
            tr_data = json.load(f)
        apply_trans(dir, tr_data)
