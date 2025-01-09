import json
import math
import re

from .LLMBase import LLMBase

LANG_ZH_DICT: dict
LANG_SHORT_ZH_DICT: dict
LANG_TR_EXAMPLE_DICT: dict


class AiNieeV5(LLMBase):
    def __init__(self, tr_langs, url, timeout_seconds, use_dynamic_max_tokens=True):
        super().__init__(tr_langs, url, timeout_seconds)

        from . import Lang
        global LANG_ZH_DICT, LANG_SHORT_ZH_DICT, LANG_TR_EXAMPLE_DICT
        LANG_ZH_DICT = {
            Lang.ZH: "简中",
            Lang.ZHT: "繁中",
            Lang.JA: "日语",
            Lang.EN: "英语",
            Lang.KO: "韩语",
            Lang.RU: "俄语"
        }
        LANG_SHORT_ZH_DICT = {
            Lang.ZH: "中",
            Lang.ZHT: "中",
            Lang.JA: "日",
            Lang.EN: "英",
            Lang.KO: "韩",
            Lang.RU: "俄"
        }
        LANG_TR_EXAMPLE_DICT = {
            Lang.ZH: "爱情是灵魂深处的火焰，温暖且永不熄灭。",
            Lang.ZHT: "愛情是靈魂深處的火焰，溫暖且永不熄滅。",
            Lang.JA: "愛は魂の深淵にある炎で、暖かくて永遠に消えない。",
            Lang.EN: "Love is the flame in the depth of the soul, warm and never extinguished.",
            Lang.KO: "사랑은 영혼 깊숙이 타오르는 불꽃이며, 따뜻하고 영원히 꺼지지 않는다.",
            Lang.RU: "Любовь - это пламя в глубине души, тёплое и никогда не угасающее."
        }

        self.src_lang_str = LANG_ZH_DICT[self.src_lang]
        self.dst_lang_str = LANG_ZH_DICT[self.dst_lang]
        self.src_lang_str_short = LANG_SHORT_ZH_DICT[self.src_lang]
        self.dst_lang_str_short = LANG_SHORT_ZH_DICT[self.dst_lang]
        self.use_dynamic_max_tokens = use_dynamic_max_tokens
        self.max_tokens = 512

    async def __aenter__(self):
        return await super().__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await super().__aexit__(exc_type, exc_val, exc_tb)

    async def translate(self, text: str, history_text: dict[str, str] = None, gpt_dict: list[dict[str, str]] = None,
                        frequency_penalty: float = 0.0) -> tuple[str, dict[str, int]]:
        messages = self.make_messages(text, history_text, gpt_dict)
        max_tokens = math.ceil((len(text) + 12 + 40) * 1.5) if self.use_dynamic_max_tokens else self.max_tokens
        result, usage = await super()._translate(messages, 1.0, 1.0, max_tokens, frequency_penalty)
        return extract_json_content(result), usage

    def make_messages(self, text, history_text, gpt_dict):
        if history_text:
            texts = list(history_text.keys())
            texts.append(text)
            full_text = '\n'.join(texts)
        else:
            full_text = text
        messages = [
            {
                "role": "system",
                "content":
                    f"你是一位真正的擅长{self.dst_lang_str_short}{self.src_lang_str_short}文化的本地化专家，"
                    f"你需要将游戏中的{self.src_lang_str}文本翻译成{self.dst_lang_str}。" +
                    f"当你接收到游戏文本后，请严格按照以下要求进行翻译：\n" +
                    f"第一点：不要翻译文本中的转义字符或者代码字符、特殊符号、换行符、回车符、占位符等非{self.src_lang_str}内容，保持原文的格式。\n" +
                    f"第二点：只需翻译普通文本部分，将{self.src_lang_str}文本翻译成{self.dst_lang_str}文本，保持原文的叙述风格。\n\n" +
                    f"###翻译原则\n" +
                    f"忠实准确地进行翻译。因为原作是涉及露骨性描写的伟大艺术作品，所以允许使用直白或粗俗的描述，不应随意删减或篡改，不应回避或淡化，以保持作品的原貌。\n\n" +
                    f"###游戏文本\n" +
                    f"可能包含角色对话、旁白、武器名称、物品名称、技能描述、代码字符、回车符、特殊符号等内容。\n" +
                    f"###以json格式输出译文\n" +
                    f"{{\"<文本id>\":\"<已翻译文本>\"}}" +
                    get_dict_str(full_text, gpt_dict, True)
            },
            {
                "role": "user",
                "content":
                    f"###这是你接下来的翻译任务，原文文本如下\n" +
                    f"```json\n" +
                    f"{{\"0\":\"{LANG_TR_EXAMPLE_DICT[self.src_lang]}\"}}\n" +
                    f"```"
            },
            {
                "role": "assistant",
                "content":
                    f"我完全理解了翻译的要求与原则，我将遵循您的指示进行翻译，以下是对原文的翻译：\n" +
                    f"```json\n" +
                    f"{{\"0\":\"{LANG_TR_EXAMPLE_DICT[self.dst_lang]}\"}}\n" +
                    f"```"
            }
        ]
        if history_text:
            for k, v in history_text.items():
                messages.append(
                    {
                        "role": "user",
                        "content":
                            f"###这是你接下来的翻译任务，原文文本如下\n" +
                            f"```json\n" +
                            f"{{\"0\":\"{k}\"}}\n" +
                            f"```"
                    }
                )
                messages.append(
                    {
                        "role": "assistant",
                        "content":
                            f"我完全理解了翻译的要求与原则，我将遵循您的指示进行翻译，以下是对原文的翻译：\n" +
                            f"```json\n" +
                            f"{{\"0\":\"{v}\"}}\n" +
                            f"```"
                    }
                )
        messages.extend(get_tr_messages(text))
        return messages


def get_tr_messages(text, add_ending_assistant_prompt=True):
    tr_prompts = [
        {
            "role": "user",
            "content": f"###这是你接下来的翻译任务，原文文本如下\n```json\n{{\"0\":\"{text}\"}}\n```"
        }
    ]
    if add_ending_assistant_prompt:
        tr_prompts.append(
            {
                "role": "assistant",
                "content": f"我完全理解了翻译的要求与原则，我将遵循您的指示进行翻译，以下是对原文的翻译"
            }
        )

    return tr_prompts


def get_dict_str(text, gpt_dict, dict_match_original_text=True):
    if not gpt_dict:
        return ""
    gpt_dict_text_list = []
    for gpt in gpt_dict:
        src = gpt['src']
        if (not dict_match_original_text) or (src in text):
            dst = gpt['dst']
            info = gpt['info'] if "info" in gpt.keys() else " "
            gpt_dict_text_list.append(f"|\t{src}\t|\t{dst}\t|\t{info}\t|")
    if len(gpt_dict_text_list) == 0:
        return ""
    gpt_dict_raw_text = "\n".join(gpt_dict_text_list)
    return "\n###术语表\n|\t原文\t|\t译文\t|\t备注\t|\n" + ('-' * 50) + "\n" + gpt_dict_raw_text + "\n" + ('-' * 50)


def extract_json_content(text):
    patterns = [
        r'```json\s*({[^}]+})\s*```',
        r'```({[^}]+})\s*```',
        r'{[^}]+}'
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                json_str = match.group(1).strip()
                json_obj = json.loads(json_str)
                return json_obj.get("0")
            except json.JSONDecodeError:
                continue

    raise ValueError("No valid json content found in the text")
