from traceback import print_exc
import requests

from sakurallm.sakura import sakura_strip

# OpenAI
# from openai import OpenAI


history = {
    "ja": [],
    "zh": []
}
session = requests.Session()
config = {
    'API接口地址': "http://192.168.7.119:40053",
    'API超时(秒)': 120,
    '利用上文信息翻译（通常会有一定的效果提升，但会导致变慢）': False,
    '附带上下文个数（必须打开利用上文翻译）': 3,
    'temperature': 0.1,
    'top_p': 0.3,
    'num_beams': 1,
    'do_sample': True,
    'max_new_token': 384,
    'repetition_penalty': 1,
    'frequency_penalty': 0,
    'fix_degeneration': True,
}


# def init():
#     global config
#     config = {
#         'API接口地址': "http://192.168.5.18:40050/",
#         'API超时(秒)': 30,
#         '利用上文信息翻译（通常会有一定的效果提升，但会导致变慢）': False,
#         '附带上下文个数（必须打开利用上文翻译）': 3,
#         'temperature': 0.1,
#         'top_p': 0.3,
#         'num_beams': 1,
#         'do_sample': True,
#         'max_new_token': 512,
#         'repetition_penalty': 1,
#         'frequency_penalty': 0,
#         'fix_degeneration': True,
#     }


def sliding_window(text_ja, text_zh):
    if text_ja == "" or text_zh == "":
        return
    history['ja'].append(text_ja)
    history['zh'].append(text_zh)
    if len(history['ja']) > int(config['附带上下文个数（必须打开利用上文翻译）']) + 1:
        del history['ja'][0]
        del history['zh'][0]


def get_history(key):
    prompt = ""
    for q in history[key]:
        prompt += q + "\n"
    prompt = prompt.strip()
    return prompt


def get_client(api_url):
    if api_url[-4:] == "/v1/":
        api_url = api_url[:-1]
    elif api_url[-3:] == "/v1":
        pass
    elif api_url[-1] == '/':
        api_url += "v1"
    else:
        api_url += "/v1"
    # OpenAI
    # client = OpenAI(api_key="114514", base_url=api_url)
    return api_url


def make_messages(query, is_rpg=False, gpt_dict=None, history_ja=None, history_zh=None, **kwargs):
    gpt_dict_text_list = []
    gpt_dict_raw_text = ""
    if gpt_dict is not None:
        for gpt in gpt_dict:
            src = gpt['src']
            dst = gpt['dst']
            info = gpt['info'] if "info" in gpt.keys() else None
            if info:
                single = f"{src}->{dst} #{info}"
            else:
                single = f"{src}->{dst}"
            gpt_dict_text_list.append(single)
        gpt_dict_raw_text = "\n".join(gpt_dict_text_list)
    if not is_rpg:
        messages = [
            {
                "role": "system",
                "content": "你是一个轻小说翻译模型，可以流畅通顺地以日本轻小说的风格将日文翻译成简体中文，"
                           "并联系上下文正确使用人称代词，不擅自添加原文中没有的代词。"
            }
        ]
    else:
        messages = [
            {
                "role": "system",
                "content": "你是一个游戏翻译模型，可以流畅通顺地以日本RPG游戏的风格将日文翻译成简体中文，"
                           "并联系上下文正确使用人称代词，不擅自添加原文中没有的代词，也不要翻译英文。"
            }
        ]
    user_prompt = "将下面的日文文本翻译成中文：" + query
    messages.append(
        {
            "role": "user",
            "content": user_prompt
        }
    )
    return messages


def send_request(query, api_url=None, is_rpg=False, gpt_dict=None, is_test=False, **kwargs):
    if api_url is None:
        api_url = config['API接口地址']
    api_url = get_client(api_url)
    timeout = config['API超时(秒)']
    extra_query = {
        'do_sample': bool(config['do_sample']),
        'num_beams': int(config['num_beams']),
        'repetition_penalty': float(config['repetition_penalty']),
    }
    messages = make_messages(query, is_rpg=is_rpg, gpt_dict=gpt_dict, **kwargs)
    try:
        # OpenAI
        # output = client.chat.completions.create(
        data = dict(
            model="sukinishiro",
            # model="sakura1b8",
            messages=messages,
            temperature=float(config['temperature']),
            top_p=float(config['top_p']),
            max_tokens=1 if is_test else int(config['max_new_token']),
            frequency_penalty=float(kwargs['frequency_penalty']) if "frequency_penalty" in kwargs.keys() else float(
                config['frequency_penalty']),
            seed=-1,
            extra_query=extra_query,
            stream=False,
        )
        output = session.post(api_url + "/chat/completions", timeout=timeout, json=data).json()
    except requests.Timeout as e:
        raise ValueError(f"连接到Sakura API超时：{api_url}，当前最大连接时间为: {timeout}，请尝试修改参数。")

    except Exception as e:
        print(e)
        raise ValueError(
            f"无法连接到Sakura API：{api_url}，请检查你的API链接是否正确填写，以及API后端是否成功启动。")
    return output


def translate(query, api_url=None, is_rpg=False, gpt_dict=None):
    query = query.strip()

    global history
    if not config['API接口地址']:
        raise ValueError("API接口地址未设置")
    history = {
        "ja": [],
        "zh": []
    }
    frequency_penalty = float(config['frequency_penalty'])
    if not bool(config['利用上文信息翻译（通常会有一定的效果提升，但会导致变慢）']):
        output = send_request(query, api_url=api_url, is_rpg=is_rpg, gpt_dict=gpt_dict)
        completion_tokens = output["usage"]["completion_tokens"]
        output_text = output["choices"][0]["message"]["content"]

        if bool(config['fix_degeneration']):
            cnt = 0
            while completion_tokens == int(config['max_new_token']):
                # detect degeneration, fixing
                frequency_penalty += 0.1
                output = send_request(query, api_url=api_url, frequency_penalty=frequency_penalty, is_rpg=is_rpg, gpt_dict=gpt_dict)
                completion_tokens = output["usage"]["completion_tokens"]
                output_text = output["choices"][0]["message"]["content"]
                cnt += 1
                if cnt == 2:
                    break
    else:
        # 实验性功能，测试效果后决定是否加入。
        # fallback = False
        # if config['启用日文上下文模式']:
        #     history_prompt = get_history('ja')
        #     output = send_request(history_prompt + "\n" + query)
        #     completion_tokens = output.usage.completion_tokens
        #     output_text = output.choices[0].message.content

        #     if len(output_text.split("\n")) == len(history_prompt.split("\n")) + 1:
        #         output_text = output_text.split("\n")[-1]
        #     else:
        #         fallback = True
        # 如果日文上下文模式失败，则fallback到中文上下文模式。
        # if fallback or not config['启用日文上下文模式']:

        history_prompt = get_history('zh')
        output = send_request(query, api_url=api_url, history_zh=history_prompt, is_rpg=is_rpg, gpt_dict=gpt_dict)
        completion_tokens = output["usage"]["completion_tokens"]
        output_text = output["choices"][0]["message"]["content"]

        if bool(config['fix_degeneration']):
            cnt = 0
            while completion_tokens == int(config['max_new_token']):
                frequency_penalty += 0.1
                output = send_request(query, api_url=api_url, history_zh=history_prompt, frequency_penalty=frequency_penalty, is_rpg=is_rpg, gpt_dict=gpt_dict)
                completion_tokens = output["usage"]["completion_tokens"]
                output_text = output["choices"][0]["message"]["content"]
                cnt += 1
                if cnt == 3:
                    output_text = "Error：模型无法完整输出或退化无法解决，请调大设置中的max_new_token！！！原输出：" + output_text
                    break
        sliding_window(query, output_text)

    output_text = sakura_strip(query, output_text)

    return output_text


def translate_rpg(query, api_url=None, is_rpg=True, gpt_dict=None):
    return translate(query, api_url=api_url, is_rpg=is_rpg, gpt_dict=gpt_dict)
