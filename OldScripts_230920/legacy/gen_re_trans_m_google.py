import json
import time
from urllib.parse import urlencode

import requests
from google_batch import Translator


def need_re_trans(v):
    need_rt = False
    if len(v) == 0:
        need_rt = True
    elif 'sorry' in v or 'Sorry' in v:
        need_rt = True
    elif 'apologize' in v or 'Apologize' in v:
        need_rt = True
    elif 'ascii' in v or 'ASCII' in v:
        need_rt = True
    elif 'japanese' in v or 'Japanese' in v:
        need_rt = True
    elif 'simplified' in v or 'Simplified' in v:
        need_rt = True
    elif 'chinese' in v or 'Chinese' in v:
        need_rt = True
    elif 'can\'t' in v or 'cannot' in v:
        need_rt = True
    elif '无法提供' in v or '不能提供' in v:
        need_rt = True
    elif '简体中文' in v:
        need_rt = True
    elif '似乎没有需要' in v:
        need_rt = True
    elif '版权' in v:
        need_rt = True
    return need_rt


# translator = Translator(proxies='http://127.0.0.1:10809')


ss = requests.session()

_ = ss.get('https://translate.google.com/', headers={
            'authority': 'translate.google.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'sec-ch-ua': '"Microsoft Edge";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
            'sec-ch-ua-arch': '"x86"',
            'sec-ch-ua-bitness': '"64"',
            'sec-ch-ua-full-version': '"105.0.1343.53"',
            'sec-ch-ua-full-version-list': '"Microsoft Edge";v="105.0.1343.53", "Not)A;Brand";v="8.0.0.0", "Chromium";v="105.0.5195.127"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"10.0.0"',
            'sec-ch-ua-wow64': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.53',
        }, verify=False, proxies={'http':'http://127.0.0.1:10809', 'https':'http://127.0.0.1:10809'}).text
        # print(html)
        # self.bl=re.search('"cfb2h":"(.*?)"',html).groups()[0]
        # self.fsid=re.search('"FdrFJe":"(.*?)"',html).groups()[0]

def realfy1(content):
        t1 = time.time()
        param = json.dumps([[content, 'ja', 'zh-cn', True], [1]])
        # print([content, 'ja', 'zh-CN', True])
        freq = json.dumps([[['MkEWBc', param, None, "generic"]]])
        freq = {'f.req': freq}
        freq = urlencode(freq)
        # print(freq)
        # params = {
        #     'rpcids': 'MkEWBc',
        #     'source-path': '/',
        #     'f.sid': self.fsid,
        #     'bl': self.bl,
        #     'hl': 'zh-CN',
        #     'soc-app': '1',
        #     'soc-platform': '1',
        #     'soc-device': '1',
        #     '_reqid': '86225',
        #     'rt': 'c',
        # }

        headers = {'Origin': 'https://translate.google.com', 'Referer': 'https://translate.google.com',
                   'X-Requested-With': 'XMLHttpRequest',
                   'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}

        response = ss.post('https://translate.google.com/_/TranslateWebserverUi/data/batchexecute', verify=False,
                                headers=headers, data=freq, proxies={'http':'http://127.0.0.1:10809', 'https':'http://127.0.0.1:10809'})
        # good=response.text.split('\n')[3]
        # print(response.text)
        json_data = json.loads(response.text[6:])
        data = json.loads(json_data[0][2])
        return ' '.join([x[0] for x in (data[1][0][0][5] or data[1][0])])

def translate(content):
        s = realfy1(content)
        # print(s,time.time()-t1)
        return s


result = {}
result2 = {}

f2 = open('r/re_trans_m.json', encoding='utf8')
re_trans_data_m = json.load(f2)

for k, v in re_trans_data_m.items():
    if need_re_trans(v):
        print('trans: ' + k)
        result[k] = translate(k)
        result2[k] = translate(k)
    else:
        result[k] = v

with open('r/re_trans_m_gen_google.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(result, ensure_ascii=False, indent=4))
with open('r/re_trans_m_gen_google2.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(result2, ensure_ascii=False, indent=4))
