import json

from utils.is_cjk_str import is_cjk_str

f = open('ManualTransFile.json', encoding='utf8')
mtool_trans_raw = json.load(f)

f = open('Map999.template.json', encoding='utf8')
result_raw = json.load(f)

event_id = 1

for key in mtool_trans_raw:
    if is_cjk_str(key):
        temp_event_dict = {
            "id": event_id,
            "name": key
        }
        result_raw["events"].append(temp_event_dict)
        event_id = event_id + 1

with open('c/i/Map999.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(result_raw, ensure_ascii=False))
# with open('c/i/ip.json', 'w', encoding='utf8') as f3:
#     f3.writelines(json.dumps(result_raw, ensure_ascii=False, indent=4))

