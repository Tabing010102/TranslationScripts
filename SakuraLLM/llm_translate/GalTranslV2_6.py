import math

from llm_translate.LLMBase import LLMBase


class GalTranslV2_6(LLMBase):
    def __init__(self, url, client_timeout, use_dynamic_max_tokens=True):
        super().__init__(url, client_timeout)
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
        return await super()._translate(messages, 0.2, 0.8, max_tokens, frequency_penalty)


# history_text: jp -> zh dict
def make_messages(text, history_text, gpt_dict):
    messages = [
        {
            "role": "system",
            "content": "你是一个视觉小说翻译模型，可以通顺地使用给定的术语表以指定的风格将日文翻译成简体中文，并联系上下文正确使用人称代词，注意不要混淆使役态和被动态的主语和宾语，不要擅自添加原文中没有的特殊符号，也不要擅自增加或减少换行。"
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

    user_prompt = ("参考以下术语表（可为空，格式为src->dst #备注）：\n" + gpt_dict_raw_text + "\n\n"
                   + "根据上述术语表的对应关系和备注，结合历史剧情和上下文，以流畅的风格将下面的文本从日文翻译成简体中文：" + text)

    return user_prompt
