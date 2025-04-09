import base64
import secrets
from io import BytesIO

import aiohttp
from PIL import Image
from config import api_image


async def generate_image(prompt: str):
    # URL API (если webui запущен локально, по умолчанию порт 7860)
    api_url = f"{api_image}sdapi/v1/txt2img"

    # Параметры генерации изображения
    payload = {
        "prompt": prompt,
        "steps": 50,
        "cfg_scale": 7.5,
        "width": 512,
        "height": 512
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, json=payload) as response:
            if response.status == 200:
                result = await response.json()
                # Извлекаем первое изображение из ответа
                b64_image = result["images"][0]
                image_data = base64.b64decode(b64_image)
                image = Image.open(BytesIO(image_data))
                name = "images/" + secrets.token_hex(32) + ".png"
                image.save(name)
                return name
            else:
                print("Ошибка запроса. Код статуса:", response.status)
                print("Ответ сервера:", await response.text())
