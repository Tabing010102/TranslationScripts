import json
import threading
import time

import requests

import utils
from sakurallm.sakura import translate_gal
from sakurallm.sakura.v010 import translate as translate_v010, translate_rpg as translate_rpg_v010
from sakurallm.sakura.v010_32b import translate as translate_v010_32b
from sakurallm.sakura.v090_32b import translate as translate_v090_32b

######################################################################
######################################################################


# print(translate("下層のマフィアを通じて国外で売買して、隠し財産を築いていたの"))
# while True:
#     print(translate("""「待ってろドラゴン、ステーキにしてやる！」
#
#     ダンジョンの奥深くでドラゴンに襲われ、金と食料を失ってしまった冒険者・ライオス一行。
#     再びダンジョンに挑もうにも、このまま行けば、途中で飢え死にしてしまう。
#     そこでライオスは決意する。「そうだ、モンスターを食べよう！」
#     スライム、バジリスク、ミミック、そしてドラゴン！
#     襲い来る凶暴なモンスターを食べながら、ダンジョンの踏破を目指せ！冒険者よ！
#     """))
full_dict = None
raw_dict = None
try:
    f = open('dict.json', encoding='utf8')
    raw_dict = json.load(f)
    full_dict = []
    for k, v in raw_dict.items():
        if isinstance(v, str):
            full_dict.append({"src": k, "dst": v})
        elif isinstance(v, list) and len(v) == 1:
            full_dict.append({"src": k, "dst": v[0]})
        else:
            full_dict.append({"src": k, "dst": v[0], "info": v[1]})
except:
    print("load dict failed")
    full_dict = None
f = open('msg.json', encoding='utf8')
ori_data = json.load(f)
total_lines = len(ori_data) + 2
ori_data_key_list = list(ori_data.keys())
ori_data_key_list_idx = 0
rlock = threading.Lock()
wlock = threading.Lock()
result = {}

# load existed progress
existed_data = {}
try:
    f = open('msg_tr_prog.json', encoding='utf8')
    existed_data = json.load(f)
except Exception as ex:
    print("load existed progress failed: " + str(ex))


def is_existed(key):
    if key in existed_data:
        return True
    return False


def trans_thread(endpoint, thread_id, save_progress=False):
    global ori_data_key_list_idx
    while True:
        # get next key
        rlock.acquire()
        if ori_data_key_list_idx >= len(ori_data_key_list):
            rlock.release()
            print('T#' + str(thread_id) + ' done')
            break
        cur_idx = ori_data_key_list_idx
        ori_data_key_list_idx = ori_data_key_list_idx + 1
        cur_key = ori_data_key_list[cur_idx]
        rlock.release()
        # judge if is cjk str
        if not utils.is_cjk_str(cur_key):
            print("T#" + str(thread_id) + " L[" + str(cur_idx + 2) + "/" + str(total_lines) + "]: " + cur_key + " -> skipped")
            continue
        # judge if is existed
        if is_existed(cur_key):
            print("T#" + str(thread_id) + " L[" + str(cur_idx + 2) + "/" + str(total_lines) + "]: " + cur_key + " -> existed")
            wlock.acquire()
            result[cur_key] = existed_data[cur_key]
            wlock.release()
            continue
        # translate
        cur_result = ""
        while True:
            try:
                cur_dict = None
                if raw_dict is not None:
                    cur_dict = []
                    for k, v in raw_dict.items():
                        if k in cur_key:
                            if isinstance(v, str):
                                cur_dict.append({"src": k, "dst": v})
                            elif isinstance(v, list) and len(v) == 1:
                                cur_dict.append({"src": k, "dst": v[0]})
                            else:
                                cur_dict.append({"src": k, "dst": v[0], "info": v[1]})
                    if cur_dict.__len__() == 0:
                        cur_dict = None
                # v0.9
                # cur_result = translate_gal(cur_key, endpoint + '/v1/')
                # v0.10
                # cur_result = translate_v010(cur_key, api_url=endpoint, gpt_dict=full_dict)
                # cur_result = translate_v010(cur_key, api_url=endpoint, gpt_dict=cur_dict)
                # cur_result = translate_v010(cur_key, api_url=endpoint, gpt_dict=None)
                # 0.10p1 32b
                cur_result = translate_v010_32b(cur_key, api_url=endpoint, gpt_dict=full_dict)
                # cur_result = translate_v090_32b(cur_key, api_url=endpoint)
                break
            except Exception as e:
                sleep_secs = 2
                print("T#" + str(thread_id) + " Error: " + str(e))
                print("T#" + str(thread_id) + " Sleeping for " + str(sleep_secs) + " secs")
                time.sleep(sleep_secs)
                continue
        # save to result
        wlock.acquire()
        result[cur_key] = cur_result
        print("T#" + str(thread_id) + " L[" + str(cur_idx + 2) + "/" + str(total_lines) + "]: " + cur_key + " -> " + cur_result)
        if save_progress and cur_idx % 200 == 0:
            print("T#" + str(thread_id) + " L[" + str(cur_idx + 2) + "] saving progress")
            with open('msg_tr_prog.json', 'w', encoding='utf8') as f4:
                f4.writelines(json.dumps(result, ensure_ascii=False, indent=4))
        wlock.release()
        continue


THREADS_NUM = 8
threads = []
endpoints = [
    "http://192.168.7.119:40050/",
    "http://192.168.7.119:40050/",
]
for i in range(THREADS_NUM):
    t = threading.Thread(target=trans_thread, args=(endpoints[i], "{:02d}".format(i), True))
    threads.append(t)
    t.start()
for i in range(THREADS_NUM):
    threads[i].join()

# with open('a/r/sr.json', 'w', encoding='utf8') as f3:
#     f3.writelines(json.dumps(result, ensure_ascii=False))
with open('msg_tr.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(result, ensure_ascii=False, indent=4))
