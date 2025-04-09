from ollama import AsyncClient

from config import api_gpt
from .normalization_of_the_text import normalization_of_the_text


async def request_to_text_ai(message: str) -> str:
    message = {'role': 'user', 'content': message}
    answer = ""
    async for part in await AsyncClient(host=api_gpt).chat(model='deepseek-r1:7b',
                                                           messages=[message],
                                                           stream=True):
        answer += part['message']['content']
    return normalization_of_the_text(answer)
    # return normalization_of_the_text(answer)
