class LLMBase:
    def __init__(self, endpoint_url, session):
        self.endpoint_url = endpoint_url
        self.session = session

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
        async with self.session.post(self.endpoint_url + "/chat/completions", json=req, encoding='utf8') as response:
            response = await response.json()
            return response['choices'][0]['message']['content'], response['usage']
