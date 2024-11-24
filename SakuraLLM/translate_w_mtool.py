import asyncio
import json
import os

import aiohttp
from tqdm import tqdm

import llm_translate
from util.ReadWriteLock import ReadWriteLock
from util.is_cjk_str import is_cjk_str

WORKING_DIR = 'w'
IN_FILE = 'ManualTransFile.json'
PROGRESS_FILE = 'ManualTransFile_tr_prog.json'
OUT_FILE = 'sp.json'
DICT_FILE = 'dict.json'
ENDPOINTS = [
    ['http://127.0.0.1:8080/v1/chat/completions', 16],
]
MODEL_NAME = 'LLMBase'

g_rw_lock = ReadWriteLock()
g_ori_data = {}
g_data = {}
g_un_trans_data = []
g_dict = []


async def trans_task(endpoint, task_id, session, pbar):
    global g_rw_lock
    global g_data
    global g_un_trans_data
    global g_dict
    with llm_translate.get_instance(MODEL_NAME)(endpoint, session) as translate_instance:
        while True:
            async with g_rw_lock.read_lock():
                cur_text = next((k for k in g_un_trans_data if k not in g_data.keys()), None)
                if cur_text is None:
                    break

            cur_trans = await translate_instance.translate(cur_text, None, g_dict)

            async with g_rw_lock.write_lock():
                g_data[cur_text] = cur_trans
                pbar.update(1)
                if len(g_data) % 100 == 0:
                    with open(os.path.join(folder, PROGRESS_FILE), 'w', encoding='utf8') as f:
                        json.dump(g_data, f, ensure_ascii=False)

    print(f"Task {task_id} finished")


def init_global_data(folder):
    global g_ori_data
    global g_data
    global g_un_trans_data
    global g_dict

    g_dict = []
    with open(os.path.join(folder, DICT_FILE), encoding='utf8') as f:
        dict_raw = json.load(f)
        for k, v in dict_raw.items():
            if isinstance(v, str):
                g_dict.append({"src": k, "dst": v})
            elif isinstance(v, list) and len(v) == 1:
                g_dict.append({"src": k, "dst": v[0]})
            else:
                g_dict.append({"src": k, "dst": v[0], "info": v[1]})

    with open(os.path.join(folder, IN_FILE), encoding='utf8') as f:
        g_ori_data = json.load(f)
    with open(os.path.join(folder, PROGRESS_FILE), encoding='utf8') as f:
        g_data = json.load(f)
    for k, v in g_ori_data:
        if is_cjk_str(k) and k not in g_data:
            g_un_trans_data.append(k)


async def translate(folder):
    init_global_data(folder)

    tasks = []
    sessions = []
    with tqdm(total=len(g_un_trans_data)) as pbar:
        for i in range(len(ENDPOINTS)):
            session = aiohttp.ClientSession()
            sessions.append(session)
            for j in range(ENDPOINTS[i][1]):
                task = asyncio.create_task(trans_task(ENDPOINTS[i][0], '%05d'.format(i * 100 + j), session, pbar))
                tasks.append(task)
    print(f'Starting {len(tasks)} tasks')
    await asyncio.gather(*tasks)
    print(f'Closing sessions')
    for session in sessions:
        await session.close()


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
    for folder in get_trans_folders(WORKING_DIR):
        asyncio.run(translate(folder))
