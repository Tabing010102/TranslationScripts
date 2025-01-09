import asyncio
import json
import os

import aiohttp
from tqdm import tqdm

import llm_translate
from util.ReadWriteLock import ReadWriteLock
from util.SlidingWindowRateCalculator import SlidingWindowRateCalculator
from util.is_cjk_str import is_cjk_str
from util.sakura_util import sakura_strip

WORKING_DIR = 'w'
IN_FILE = 'ManualTransFile.json'
PROGRESS_FILE = 'ManualTransFile_tr_prog.json'
OUT_FILE = 'sp.json'
DICT_FILE = 'dict.json'
ENDPOINTS = [
    ['http://127.0.0.1:8080/v1/chat/completions', 16],
]
TIMEOUT_SECONDS = 30
SKIP_WHEN_FAILED = True
MODEL_NAME = 'SakuraV1'
SRC_LANG = llm_translate.Lang.JA
DST_LANG = llm_translate.Lang.ZH
TQDM_MIN_INTERVAL = 2.0

g_rw_lock = ReadWriteLock()
g_ori_data = {}
g_data = {}
g_un_trans_data = []
g_dict = []
g_pbar: tqdm
g_token_rate_calculator = SlidingWindowRateCalculator(10)
g_tqdm_last_set_postfix_time = asyncio.get_event_loop().time()
g_failed_lines = []


async def trans_task(endpoint, task_id):
    global g_rw_lock, g_data, g_un_trans_data, g_dict, g_pbar, g_failed_lines, g_tqdm_last_set_postfix_time, \
        g_token_rate_calculator

    session_timeout = aiohttp.ClientTimeout(total=None, sock_connect=TIMEOUT_SECONDS, sock_read=TIMEOUT_SECONDS)
    async with llm_translate.get_instance(MODEL_NAME)((SRC_LANG, DST_LANG),
                                                      endpoint, session_timeout) as translate_instance:

        while True:
            await g_rw_lock.acquire_write()
            cur_text = next((k for k in g_un_trans_data if k not in g_failed_lines and k not in g_data.keys()), None)
            if cur_text is None:
                await g_rw_lock.release_write()
                break
            g_data[cur_text] = None
            await g_rw_lock.release_write()

            if SKIP_WHEN_FAILED:
                try:
                    cur_trans, usage = await translate_instance.translate(cur_text, None, g_dict)
                except Exception as ex:
                    print(f"Task #{task_id} failed to translate {cur_text}: {ex}")
                    g_pbar.update(len(cur_text))
                    await g_rw_lock.acquire_write()
                    g_data.pop(cur_text)
                    g_failed_lines.append(cur_text)
                    await g_rw_lock.release_write()
                    continue
            else:
                while True:
                    try:
                        cur_trans, usage = await translate_instance.translate(cur_text, None, g_dict)
                        break
                    except Exception as ex:
                        print(f"Task #{task_id} failed to translate {cur_text}: {ex}\nRetrying in 1s")
                        await asyncio.sleep(1)

            cur_trans = sakura_strip(cur_text, cur_trans)

            await g_rw_lock.acquire_write()
            g_data[cur_text] = cur_trans
            g_pbar.update(len(cur_text))
            g_token_rate_calculator.add_count(usage['completion_tokens'])
            if asyncio.get_event_loop().time() - g_tqdm_last_set_postfix_time > TQDM_MIN_INTERVAL:
                g_pbar.set_postfix(tg=f'{g_token_rate_calculator.get_rate()}t/s')
                g_tqdm_last_set_postfix_time = asyncio.get_event_loop().time()
            if len(g_data) % 100 == 0:
                with open(os.path.join(trans_dir, PROGRESS_FILE), 'w', encoding='utf8') as f:
                    json.dump(g_data, f, ensure_ascii=False, indent=4)
            await g_rw_lock.release_write()

    print(f"Task {task_id} finished")


def init_global_data(trans_dir):
    global g_ori_data, g_data, g_un_trans_data, g_dict, g_pbar, g_failed_lines, g_tqdm_last_set_postfix_time, \
        g_token_rate_calculator

    g_dict = []
    try:
        with open(os.path.join(trans_dir, DICT_FILE), encoding='utf8') as f:
            dict_raw = json.load(f)
            for k, v in dict_raw.items():
                if isinstance(v, str):
                    g_dict.append({"src": k, "dst": v})
                elif isinstance(v, list) and len(v) == 1:
                    g_dict.append({"src": k, "dst": v[0]})
                else:
                    g_dict.append({"src": k, "dst": v[0], "info": v[1]})
    except Exception as ex:
        print(f"{trans_dir} load dict failed, {ex}")
        g_dict = None

    with open(os.path.join(trans_dir, IN_FILE), encoding='utf8') as f:
        g_ori_data = json.load(f)
    try:
        with open(os.path.join(trans_dir, PROGRESS_FILE), encoding='utf8') as f:
            g_data = json.load(f)
        empty_keys = [k for k, v in g_data.items() if not v]
        for k in empty_keys:
            g_data.pop(k)
        un_existed_keys = [k for k in g_data.keys() if k not in g_ori_data]
        for k in un_existed_keys:
            g_data.pop(k)
    except Exception as ex:
        print(f"{trans_dir} load progress failed: {ex}")
        g_data = {}
    g_un_trans_data = []
    for k, v in g_ori_data.items():
        if is_cjk_str(k) and k not in g_data:
            g_un_trans_data.append(k)

    trans_dir_name = trans_dir[:12] + '...' if len(trans_dir) > 15 else trans_dir
    total_un_trans_chars = sum(len(k) for k in g_un_trans_data)
    g_pbar = tqdm(total=total_un_trans_chars, desc=f'Translating {trans_dir_name}', leave=True,
                  unit='ch', mininterval=TQDM_MIN_INTERVAL)
    g_pbar.set_postfix(tg=f'?t/s')
    g_tqdm_last_set_postfix_time = asyncio.get_event_loop().time()
    g_failed_lines = []
    g_token_rate_calculator.reset()


async def translate(trans_dir):
    global g_failed_lines

    init_global_data(trans_dir)

    tasks = []
    for i in range(len(ENDPOINTS)):
        for j in range(ENDPOINTS[i][1]):
            task = asyncio.create_task(trans_task(ENDPOINTS[i][0], '{:05d}'.format(i * 100 + j)))
            tasks.append(task)
    print(f'Starting {len(tasks)} tasks')
    await asyncio.gather(*tasks)
    print(f'Saving results')
    if len(g_failed_lines) == 0:
        with open(os.path.join(trans_dir, OUT_FILE), 'w', encoding='utf8') as f:
            json.dump(g_data, f, ensure_ascii=False, indent=4)
    else:
        with open(os.path.join(trans_dir, PROGRESS_FILE), 'w', encoding='utf8') as f:
            json.dump(g_data, f, ensure_ascii=False, indent=4)


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
    for trans_dir in tqdm(get_trans_dirs(WORKING_DIR), desc=f'Processing dirs', leave=True, unit='dir'):
        asyncio.run(translate(trans_dir))
