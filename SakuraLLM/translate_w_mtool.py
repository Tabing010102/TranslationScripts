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
SKIP_WHEN_FAILED = True
MODEL_NAME = 'SakuraV1'
TQDM_MIN_INTERVAL = 1.0

g_rw_lock = ReadWriteLock()
g_ori_data = {}
g_data = {}
g_un_trans_data = []
g_dict = []
g_pbar = None
g_token_count = 0
g_tqdm_last_set_postfix_time = asyncio.get_event_loop().time()
g_failed_lines = []


async def trans_task(endpoint, task_id, session):
    global g_rw_lock, g_data, g_un_trans_data, g_dict, g_token_count, g_pbar, g_failed_lines, \
        g_tqdm_last_set_postfix_time

    translate_instance = llm_translate.get_instance(MODEL_NAME)(endpoint, session)

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
        g_token_count += usage['completion_tokens']
        if asyncio.get_event_loop().time() - g_tqdm_last_set_postfix_time > TQDM_MIN_INTERVAL:
            elapsed_time = asyncio.get_event_loop().time() - g_tqdm_last_set_postfix_time
            token_speed = g_token_count / elapsed_time if elapsed_time > 0 else 0
            g_pbar.set_postfix(tg=f'{token_speed:.2f}t/s')
            g_tqdm_last_set_postfix_time = asyncio.get_event_loop().time()
            g_token_count = 0
        if len(g_data) % 100 == 0:
            with open(os.path.join(folder, PROGRESS_FILE), 'w', encoding='utf8') as f:
                json.dump(g_data, f, ensure_ascii=False, indent=4)
        await g_rw_lock.release_write()

    print(f"Task {task_id} finished")


def init_global_data(folder):
    global g_ori_data, g_data, g_un_trans_data, g_dict, g_pbar, g_token_count,\
        g_failed_lines, g_tqdm_last_set_postfix_time

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
    except Exception as ex:
        print(f"{folder} load dict failed, {ex}")
        g_dict = None

    with open(os.path.join(folder, IN_FILE), encoding='utf8') as f:
        g_ori_data = json.load(f)
    try:
        with open(os.path.join(folder, PROGRESS_FILE), encoding='utf8') as f:
            g_data = json.load(f)
        empty_keys = [k for k, v in g_data.items() if not v]
        for k in empty_keys:
            g_data.pop(k)
    except Exception as ex:
        print(f"{folder} load progress failed: {ex}")
        g_data = {}
    for k, v in g_ori_data.items():
        if is_cjk_str(k) and k not in g_data:
            g_un_trans_data.append(k)

    folder_name = folder[:12] + '...' if len(folder) > 15 else folder
    total_un_trans_chars = sum(len(k) for k in g_un_trans_data)
    g_pbar = tqdm(total=total_un_trans_chars, desc=f'Translating {folder_name}', leave=True,
                  unit='ch', mininterval=TQDM_MIN_INTERVAL)
    g_pbar.set_postfix(tg=f'?t/s')
    g_token_count = 0
    g_tqdm_last_set_postfix_time = asyncio.get_event_loop().time()
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
    for folder in tqdm(get_trans_folders(WORKING_DIR), desc=f'Processing folders', leave=True, unit='dir'):
        asyncio.run(translate(folder))
