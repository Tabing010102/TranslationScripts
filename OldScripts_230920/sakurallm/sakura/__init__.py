import time

import requests


def make_prompt_rpg(model_type, context):
    if model_type == "baichuan":
        prompt = f"<reserved_106>将下面的日文文本翻译成中文：{context}<reserved_107>"
    elif model_type == "qwen":
        prompt = f"<|im_start|>system\n你是一个游戏翻译模型，可以流畅通顺地以日本RPG游戏的风格将日文翻译成简体中文，并联系上下文正确使用人称代词，不擅自添加原文中没有的代词，不擅自添加原文中没有的标点符号，不翻译英文。<|im_end|>\n<|im_start|>user\n将下面的日文文本翻译成中文：{context}<|im_end|>\n<|im_start|>assistant\n"
    else:
        prompt = f"<reserved_106>将下面的日文文本翻译成中文：{context}<reserved_107>"

    return prompt


def make_prompt_gal(model_type, context):
    if model_type == "baichuan":
        prompt = f"<reserved_106>将下面的日文文本翻译成中文：{context}<reserved_107>"
    elif model_type == "qwen":
        prompt = f"<|im_start|>system\n你是一个轻小说翻译模型，可以流畅通顺地以日本轻小说的风格将日文翻译成简体中文，并联系上下文正确使用人称代词，不擅自添加原文中没有的代词。<|im_end|>\n<|im_start|>user\n将下面的日文文本翻译成中文：{context}<|im_end|>\n<|im_start|>assistant\n"
    else:
        prompt = f"<reserved_106>将下面的日文文本翻译成中文：{context}<reserved_107>"

    return prompt


def make_request(api_type, prompt, is_test=False):
    if api_type == "llama.cpp":
        request = {
            "prompt": prompt,
            "n_predict": 1 if is_test else int(128),
            "temperature": float(0.10),
            "top_p": float(0.30),
            "repeat_penalty": float(1.00),
            "frequency_penalty": float(0.00),
            "top_k": 40,
            "seed": -1
        }
        return request


def do_post(api_type, api_url, model_type, request):
        try:
            response = requests.post(api_url, json=request).json()
            if api_type == "dev_server":
                output = response['results'][0]['text']
                new_token = response['results'][0]['new_token']
            elif api_type == "llama.cpp":
                output =  response['content']
                new_token = response['tokens_predicted']
            else:
                raise NotImplementedError("3")
        except Exception as e:
            raise Exception(str(e) + f"\napi_type: '{api_type}', api_url: '{api_url}', model_type: '{model_type}'\n与API接口通信失败，请检查设置的API服务器监听地址是否正确，或检查API服务器是否正常开启。")
        return output, new_token, response


def translate_rpg(query, endpoint="http://192.168.5.19:40053/"):
    api_type = "llama.cpp"
    api_url = endpoint + "completion"
    model_type = "qwen"

    prompt = make_prompt_rpg(model_type, query)
    request = make_request(api_type, prompt)

    output, new_token, _ = do_post(api_type, api_url, model_type, request)

    if bool(True):
        cnt = 0
        while new_token == 128:
            # detect degeneration, fixing
            request['frequency_penalty'] += 0.1
            output, new_token, _ = do_post(api_type, api_url, model_type, request)

            cnt += 1
            if cnt == 2:
                break
    output = output.strip()
    output = sakura_strip(query, output)
    return output


def translate_gal(query, endpoint="http://192.168.5.18:40053/"):
    api_type = "llama.cpp"
    api_url = endpoint + "completion"
    model_type = "qwen"

    prompt = make_prompt_gal(model_type, query)
    request = make_request(api_type, prompt)

    output, new_token, _ = do_post(api_type, api_url, model_type, request)

    if bool(True):
        cnt = 0
        while new_token == 128:
            # detect degeneration, fixing
            request['frequency_penalty'] += 0.1
            output, new_token, _ = do_post(api_type, api_url, model_type, request)

            cnt += 1
            if cnt == 2:
                break
    output = output.strip()
    output = sakura_strip(query, output)
    return output


def translate_ensured(query):
    cnt_result = ""
    while True:
        try:
            cnt_result = translate_rpg(query)
            break
        except Exception as e:
            sleep_secs = 2
            print("Error: " + str(e))
            print("Sleeping for " + str(sleep_secs) + " secs")
            time.sleep(sleep_secs)
            continue
    return cnt_result


def sakura_strip(k, v):
    if len(k) < 2 or len(v) < 2:
        return v
    if k[0] != '「' and v[0] == '「':
        v = v[1:]
    if k[-1] != '」' and v[-1] == '」':
        v = v[:-1]
    if len(v) < 2:
        return v
    if k[-1] == '」' and k[-2] != '。' and k[-2] != '？' and k[-2] != '！' and v[-2] == '。':
        v = v[:-2] + v[-1]
    if k[-1] != '」' and k[-1] != '。' and k[-1] != '？' and k[-1] != '！' and v[-1] == '。':
        v = v[:-1]
    return v
