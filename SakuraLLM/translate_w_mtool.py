import asyncio
import json
import os

import aiohttp
from tqdm import tqdm

import llm_translate
from util.ReadWriteLock import ReadWriteLock
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
MODEL_NAME = 'SakuraV1'

g_rw_lock = ReadWriteLock()
g_ori_data = {}
g_data = {}
g_un_trans_data = []
g_dict = []
g_pbar = None
g_token_count = 0
g_start_time = None
g_failed_lines = []


async def trans_task(endpoint, task_id, session):
    global g_rw_lock, g_data, g_un_trans_data, g_dict, g_token_count, g_start_time, g_pbar, g_failed_lines

    translate_instance = llm_translate.get_instance(MODEL_NAME)(endpoint, session)

    while True:
        await g_rw_lock.acquire_write()
        cur_text = next((k for k in g_un_trans_data if k not in g_failed_lines and k not in g_data.keys()), None)
        if cur_text is None:
            break
        g_data[cur_text] = None
        await g_rw_lock.release_write()

        try:
            cur_trans, usage = await translate_instance.translate(cur_text, None, g_dict)
        except Exception as e:
            print(f"Task #{task_id} failed to translate {cur_text}: {e}")
            await g_rw_lock.acquire_write()
            del g_data[cur_text]
            g_failed_lines.append(cur_text)
            await g_rw_lock.release_write()
            continue

        cur_trans = sakura_strip(cur_text, cur_trans)

        await g_rw_lock.acquire_write()
        g_data[cur_text] = cur_trans
        g_pbar.update(1)
        g_token_count += usage['completion_tokens']
        elapsed_time = (asyncio.get_event_loop().time() - g_start_time)
        token_speed = g_token_count / elapsed_time if elapsed_time > 0 else 0
        g_pbar.set_postfix(tg=f'{token_speed:.2f}t/s')
        if len(g_data) % 100 == 0:
            with open(os.path.join(folder, PROGRESS_FILE), 'w', encoding='utf8') as f:
                json.dump(g_data, f, ensure_ascii=False, indent=4)
        await g_rw_lock.release_write()

    print(f"Task {task_id} finished")


def init_global_data(folder):
    global g_ori_data, g_data, g_un_trans_data, g_dict, g_pbar, g_token_count, g_start_time, g_failed_lines

    g_dict = []
    try:
        with open(os.path.join(folder, DICT_FILE), encoding='utf8') as f:
            dict_raw = json.load(f)
            for k, v in dict_raw.items():
                if isinstance(v, str):
                    g_dict.append({"src": k, "dst": v})
                elif isinstance(v, list) and len(v) == 1:
                    g_dict.append({"src": k, "dst": v[0]})
                else:
                    g_dict.append({"src": k, "dst": v[0], "info": v[1]})
    except:
        print("load dict failed")
        g_dict = None

    with open(os.path.join(folder, IN_FILE), encoding='utf8') as f:
        g_ori_data = json.load(f)
    try:
        with open(os.path.join(folder, PROGRESS_FILE), encoding='utf8') as f:
            g_data = json.load(f)
    except:
        print("load progress failed")
        g_data = {}
    for k, v in g_ori_data.items():
        if is_cjk_str(k) and k not in g_data:
            g_un_trans_data.append(k)

    g_pbar = tqdm(total=len(g_un_trans_data), desc=f'Translating {folder}', leave=True, ncols=100, unit='line', mininterval=1)
    g_token_count = 0
    g_start_time = asyncio.get_event_loop().time()
    g_failed_lines = []


async def translate(folder):
    global g_failed_lines

    init_global_data(folder)

    tasks = []
    sessions = []
    for i in range(len(ENDPOINTS)):
        session_timeout = aiohttp.ClientTimeout(total=None, sock_connect=TIMEOUT_SECONDS, sock_read=TIMEOUT_SECONDS)
        session = aiohttp.ClientSession(timeout=session_timeout)
        sessions.append(session)
        for j in range(ENDPOINTS[i][1]):
            task = asyncio.create_task(trans_task(ENDPOINTS[i][0], '{:05d}'.format(i * 100 + j), session))
            tasks.append(task)
    print(f'Starting {len(tasks)} tasks')
    await asyncio.gather(*tasks)
    print(f'Closing sessions')
    for session in sessions:
        await session.close()
    if len(g_failed_lines) == 0:
        with open(os.path.join(folder, OUT_FILE), 'w', encoding='utf8') as f:
            json.dump(g_data, f, ensure_ascii=False, indent=4)
    else:
        with open(os.path.join(folder, PROGRESS_FILE), 'w', encoding='utf8') as f:
            json.dump(g_data, f, ensure_ascii=False, indent=4)


def get_trans_folders(folder):
    matching_folders = []
    for root, dirs, files in os.walk(folder):
        if IN_FILE in files:
            if OUT_FILE in files:
                print(f'{root} has been translated, skipping')
            else:
                matching_folders.append(root)
    return matching_folders


if __name__ == '__main__':
    for folder in tqdm(get_trans_folders(WORKING_DIR), desc=f'Processing folders', leave=True, ncols=100, unit='dir'):
        asyncio.run(translate(folder))
