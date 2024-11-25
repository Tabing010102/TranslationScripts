import json
import os
import threading
import time

import requests

import sakurallm.sakura.v10_14b
import utils
from sakurallm.sakura import translate_rpg
from sakurallm.sakura.v010 import translate as translate_v010, translate_rpg as translate_rpg_v010
from sakurallm.sakura.v010_32b import translate_rpg as translate_rpg_v010_32b
from sakurallm.sakura.v090_32b import translate_rpg as translate_rpg_v090_32b
from sakurallm.sakura.galtransl_v2_6 import translate as translate_galtransl_v2_6
from sakurallm.sakura.v10_14b import translate as translate_v10


ori_data_key_list_idx = 0


def perform_dir_trans(cur_dir):
    global ori_data_key_list_idx
    os.chdir(cur_dir)
    if not os.path.exists('msg.json') or os.path.exists('msg_tr.json'):
        print(f"Skipping {cur_dir}")
        os.chdir('..')
        os.chdir('..')
        return

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
                    end_with_splash = False
                    if cur_key[-1] == '\\':
                        cur_key = cur_key[:-1]
                        end_with_splash = True
                    # v0.9
                    # cur_result = translate_rpg(cur_key, endpoint + '/v1/')
                    # 0.10
                    # cur_result = translate_rpg_v010(cur_key, api_url=endpoint, gpt_dict=full_dict)
                    # cur_result = translate_rpg_v010(cur_key, api_url=endpoint, gpt_dict=cur_dict)
                    # cur_result = translate_rpg_v010(cur_key, api_url=endpoint, gpt_dict=None)
                    # 0.10p1 32b
                    # cur_result = translate_rpg_v010_32b(cur_key, api_url=endpoint, gpt_dict=full_dict)
                    # 0.9.0 32b
                    # cur_result = translate_rpg_v090_32b(cur_key, api_url=endpoint)
                    # galtransl v2.6
                    # cur_result = translate_galtransl_v2_6(cur_key, api_url=endpoint, max_tokens=cur_key.__len__() * 2)
                    # 1.0 14b
                    cur_result = translate_v10(cur_key, api_url=endpoint, max_tokens=cur_key.__len__() * 2, gpt_dict=cur_dict)
                    if end_with_splash:
                        cur_key += '\\'
                        cur_result += '\\'
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


    ENDPOINTS_NUM = 1
    threads = []
    endpoints = [
        ["http://192.168.7.119:40051/", 4],
        ["http://192.168.7.119:40050/", 4],
    ]
    threads_num = 0
    for i in range(ENDPOINTS_NUM):
        for j in range(endpoints[i][1]):
            t = threading.Thread(target=trans_thread, args=(endpoints[i][0], "{:02d}".format(threads_num + j), True))
            threads.append(t)
            t.start()
        threads_num += endpoints[i][1]
    for i in range(threads_num):
        threads[i].join()

    # with open('sr.json', 'w', encoding='utf8') as f3:
    #     f3.writelines(json.dumps(result, ensure_ascii=False))
    with open('msg_tr.json', 'w', encoding='utf8') as f3:
        f3.writelines(json.dumps(result, ensure_ascii=False, indent=4))

    os.chdir('..')
    os.chdir('..')


# 遍历当前目录下的w目录中的所有一层子目录
base_dir = 'w'
for subdir in os.listdir(base_dir):
    subdir_path = os.path.join(base_dir, subdir)
    if os.path.isdir(subdir_path):
        perform_dir_trans(subdir_path)
