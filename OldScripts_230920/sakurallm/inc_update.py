import json
import time

import utils
from sakurallm.sakura import translate_rpg

f = open('ManualTransFile.json', encoding='utf8')
ori_data = json.load(f)
total_lines = len(ori_data)

f = open('r/sp.json', encoding='utf8')
result = json.load(f)

result2 = {}

i = 2
for key in ori_data:
    # if i > 30:
    #     break
    if not utils.is_cjk_str(key):
        print("L[" + str(i) + "/" + str(total_lines) + "]: " + key + " -> skipped")
        i = i + 1
        continue
    if key in result:
        result2[key] = result[key]
        print("L[" + str(i) + "/" + str(total_lines) + "]: " + key + " -> copied")
        i = i + 1
        continue
    else:
        cnt_result = ""
        while True:
            try:
                cnt_result = translate_rpg(key)
                break
            except Exception as e:
                sleep_secs = 2
                print("Error: " + str(e))
                print("Sleeping for " + str(sleep_secs) + " secs")
                time.sleep(sleep_secs)
                continue
        print("L[" + str(i) + "/" + str(total_lines) + "]: " + key + " -> " + cnt_result)
        result2[key] = cnt_result
        i = i + 1

with open('r/sr2.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(result2, ensure_ascii=False))
with open('r/sp2.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(result2, ensure_ascii=False, indent=4))
