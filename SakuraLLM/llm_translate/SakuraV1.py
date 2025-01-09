import math

from .LLMBase import LLMBase


class SakuraV1(LLMBase):
    def __init__(self, tr_langs, url, client_timeout, use_dynamic_max_tokens=True):
        super().__init__(tr_langs, url, client_timeout)
        from . import Lang
        if self.src_lang != Lang.JA or self.dst_lang != Lang.ZH:
            raise ValueError(f"Unsupported translate langs: {self.src_lang} -> {self.dst_lang}")
        self.use_dynamic_max_tokens = use_dynamic_max_tokens
        self.max_tokens = 512

    async def __aenter__(self):
        return await super().__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await super().__aexit__(exc_type, exc_val, exc_tb)

    async def translate(self, text: str, history_text: dict[str, str] = None, gpt_dict: list[dict[str, str]] = None,
                        frequency_penalty: float = 0.0) -> tuple[str, dict[str, int]]:
        messages = make_messages(text, history_text, gpt_dict)
        max_tokens = math.ceil(len(text) * 1.5) if self.use_dynamic_max_tokens else self.max_tokens
        return await super()._translate(messages, 0.1, 0.3, max_tokens, frequency_penalty)


# history_text: jp -> zh dict
def make_messages(text, history_text, gpt_dict):
    messages = [
        {
            "role": "system",
            "content": "你是一个轻小说翻译模型，可以流畅通顺地以日本轻小说的风格将日文翻译成简体中文，并联系上下文正确使用人称代词，不擅自添加原文中没有的代词。"
        }
    ]
    if history_text:
        messages.append(
            {
                "role": "user",
                "content": get_user_prompt('\n'.join(history_text.keys()), gpt_dict)
            }
        )
        messages.append(
            {
                "role": "assistant",
                "content": '\n'.join(history_text.values())
            }
        )
    messages.append(
        {
            "role": "user",
            "content": get_user_prompt(text, gpt_dict)
        }
    )
    return messages


def get_user_prompt(text, gpt_dict, dict_match_original_text=True):
    gpt_dict_text_list = []
    if gpt_dict:
        for gpt in gpt_dict:
            src = gpt['src']
            if (not dict_match_original_text) or (src in text):
                dst = gpt['dst']
                info = gpt['info'] if "info" in gpt.keys() else None
                if info:
                    single = f"{src}->{dst} #{info}"
                else:
                    single = f"{src}->{dst}"
                gpt_dict_text_list.append(single)
    gpt_dict_raw_text = "\n".join(gpt_dict_text_list)
    has_gpt_dict = gpt_dict and len(gpt_dict_text_list) > 0

    if has_gpt_dict:
        user_prompt = "根据以下术语表（可以为空）：\n" + gpt_dict_raw_text + "\n" + "将下面的日文文本根据对应关系和备注翻译成中文：" + text
    else:
        user_prompt = "将下面的日文文本翻译成中文：" + text

    return user_prompt
