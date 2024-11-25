import json
import os
import time

import requests


def translate(query, file_name):
    API_FULL_URL = 'https://p0.kamiya.dev/api/openai/v1/chat/completions'
    SECRET_KEY = 'sk-xxxxxx'
    MODEL = 'openai:gpt-3.5-turbo'

    # os.environ['https_proxy'] = 'http://127.0.0.1:10809'
    # os.environ['http_proxy'] = 'http://127.0.0.1:10809'

    temperature = 0.3

    # first translate
    message = [
        {"role": "system", "content": "You are a translator for a Japanese RPG game"},
        {"role": "user", "content": "Translate from Japanese to simplified Chinese without translating ASCII characters and only keeps the translation result"},
        {"role": "user", "content": query}
    ]
    # re trans
    # message = [
    #     {"role": "system", "content": "You are a translator for a Japanese RPG game"},
    #     {"role": "user", "content": "Translate from Japanese to simplified Chinese"},
    #     {"role": "user", "content": query}
    # ]

    headers = {
        'Authorization': 'Bearer ' + SECRET_KEY,
        'Content-Type': 'application/json',
    }

    data = '{ "model": ' + json.dumps(MODEL)\
           + ', "stream": false, "temperature": ' + json.dumps(temperature) + ', "messages": ' + json.dumps(
        message) + ' }'

    response = requests.post(API_FULL_URL, headers=headers, data=data, timeout=30)
    response = response.json()

    with open(file_name, 'w', encoding='utf8') as f3:
        f3.writelines(json.dumps(response, ensure_ascii=False))

    try:
        message = response['choices'][0]['message']['content'].replace('\n\n', '\n').strip()
        return message
    except:
        raise Exception(json.dumps(response, ensure_ascii=False))



f = open('ManualTransFile_FN.json', encoding='utf8')
raw_data = json.load(f)


START = 0
END = 9999999


result = {}
for k, v in raw_data.items():
    if int(k) < START or int(k) > END:
        continue

    log_file_name = 'r/' + str(k) + '.log'
    is_translated = False
    if os.path.exists(log_file_name):
        f2 = open(log_file_name, encoding='utf8')
        f2d = json.load(f2)
        try:
            message = f2d['choices'][0]['message']['content']
            result[k] = message
            is_translated = True
        except:
            is_translated = False
    if is_translated:
        print('skip k = ' + str(k))
        continue
    attempts = 0
    success = False

    MAX_ATTEMPTS = 3
    while attempts < MAX_ATTEMPTS and not success:
        try:
            print('trans k = ' + str(k) + ', attempt = ' + str(attempts) + ', result = ', end='')

            cr = translate(v, log_file_name)
            result[k] = cr
            print('success')
            # time.sleep(4.5)

            success = True
        except Exception as e:
            print('failed')
            try:
                if isinstance(e.args[0], str) and len(e.args[0]) > 0:
                    ed = json.loads(e.args[0])
                    if ed.get('status') == 500:
                        print('server returned 500, retrying in 30s')
                        time.sleep(30)
                else:
                    attempts += 1
                    if attempts == MAX_ATTEMPTS:
                        result[k] = 'FAILED'
                        break
            except:
                attempts += 1
                if attempts == MAX_ATTEMPTS:
                    result[k] = 'FAILED'
                    break
        except:
            attempts += 1
            if attempts == MAX_ATTEMPTS:
                result[k] = 'FAILED'
                break

with open('r/rr.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(result, ensure_ascii=False))
with open('r/rp.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(result, ensure_ascii=False, indent=4))
