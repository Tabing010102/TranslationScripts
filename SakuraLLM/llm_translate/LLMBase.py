import json

import aiohttp


class LLMBase:
    def __init__(self, tr_langs, endpoint_url, client_timeout):
        self.src_lang, self.dst_lang = tr_langs
        self.endpoint_url = endpoint_url
        self.client_timeout = client_timeout
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=self.client_timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def _translate(self, messages: list[dict[str, str]], temperature: float,
                         top_p: float, max_tokens: int, frequency_penalty: float) \
            -> tuple[str, dict[str, int]]:
        req = {
            "model": "",
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "frequency_penalty": frequency_penalty,
            "seed": -1,
            "do_sample": True,
            "num_beams": 1,
            "repetition_penalty": 1.0,
            "stream": False,
        }
        data = json.dumps(req, ensure_ascii=False)
        headers = {
            'Content-Type': 'application/json; charset=utf-8'
        }
        async with self.session.post(self.endpoint_url, data=data, headers=headers) as response:
            response = await response.json()
            return response['choices'][0]['message']['content'], response['usage']
