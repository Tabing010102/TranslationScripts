import json
import os


def read_json_files(folder):
    file_paths = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(".json"):
                file_paths.append(os.path.join(root, file))
    return file_paths


gt_output_files = read_json_files("g\\gt_output")

f = open('g\\name_tr.json', encoding='utf8')
name_tr = json.load(f)

for gt_output_file in gt_output_files:
    with open(gt_output_file, encoding='utf8') as f:
        data = json.load(f)
        for i in range(len(data)):
            # name
            if 'name' in data[i]:
                if data[i]['name'] in name_tr:
                    data[i]['name'] = name_tr[data[i]['name']]
                else:
                    print("W: untranslated \"name\": " + data[i]['name'])

    with open(gt_output_file.replace('gt_output', 'jsoncn'), 'w', encoding='utf8') as ftr:
        ftr.writelines(json.dumps(data, ensure_ascii=False, indent=4))
