import asyncio
import hashlib
import os
import sqlite3
from datetime import datetime

import speech_recognition as sr
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters.command import Command
from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
from pydub import AudioSegment

from config import storage, ip_to_web_app, token, __checking__
from funcs.generate_image import generate_image
from funcs.summarize import summarizing
from funcs.talking import talking
from funcs.translate import translate_text

load_dotenv("config.env")

bot = Bot(token=token)
dp = Dispatcher()

con = sqlite3.connect(r'db/archive_of_users.db')
cur = con.cursor()


def webminiapp_keyboard(user_id):
    checking = __checking__ + str(user_id)
    checking = hashlib.sha256(checking.encode('utf-8')).hexdigest()
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Open Mini App",
        web_app=WebAppInfo(url=f"{ip_to_web_app}?user_id={user_id}&checking={checking}"),
    )
    return builder.as_markup()


@dp.message(Command('start'))
async def start(message: types.Message):
    await message.answer(
        'Здравствуйте!\nЯ бот с искуственным интеллектом для ведения дневника воспоминаний. Тут Вы можете написать мне всё о своём дне, а после я подведу итоги и сделаю визуальный образ на основе Вашего дня.')


@dp.message(Command("clear"))
async def end(message: types.Message):
    storage[message.from_user.id] = []
    await message.answer("История переписки сброшена")


@dp.message(Command('web'))
async def web(message: types.Message):
    await message.answer(
        "Здесь Вы можете посмотреть свои воспоминания",
        reply_markup=webminiapp_keyboard(message.from_user.id)
    )


@dp.message(Command("summarize"))
async def summarize(message: types.Message):
    cur.execute(f"""CREATE TABLE IF NOT EXISTS user{message.from_user.id} (
    date TEXT,
    text TEXT,
    image TEXT
    )""")
    messages: list = storage.get(message.from_user.id)
    if messages is None or len(messages) == 0:
        await message.answer("Вы ещё ничего не рассказали о вашем дне")
        return

    date = datetime.now().strftime("%d-%m-%Y")

    cur.execute(f"SELECT * FROM user{message.from_user.id} WHERE date = '{date}'")
    data = cur.fetchall()
    print(data)
    if len(data) == 1:
        _, _answer, _photo = data[0]
        _answer = await translate_text(_answer, "ru", "en")
        messages = [_answer] + messages
        cur.execute(f"DELETE FROM user{message.from_user.id} WHERE date = '{date}'")
    print(messages)
    text = "\n\n".join(messages)
    answer = summarizing(text)
    photo_path = await generate_image(answer)
    with open(photo_path, "rb") as image:
        photo = types.BufferedInputFile(image.read(), filename=photo_path)
    answer = await translate_text(answer, "en", "ru")
    table_name = f"user{message.from_user.id}"
    cur.execute(
        f"""INSERT INTO "{table_name}" (date, text, image) VALUES (?, ?, ?)""",
        [date, answer, photo_path]
    )
    con.commit()
    await message.answer_photo(photo, caption=answer)
    storage[message.from_user.id] = []


@dp.message(F.text)
async def func(message: types.Message):
    await talking(message, message.text)


@dp.message(lambda msg: msg.voice is not None)
async def handle_voice(message: types.Message):
    file_info = await bot.get_file(message.voice.file_id)
    file_path = file_info.file_path
    ogg_file = f"voice_{message.from_user.id}.ogg"
    wav_file = f"voice_{message.from_user.id}.wav"

    await bot.download_file(file_path, destination=ogg_file)

    # Конвертация из OGG в WAV
    sound = AudioSegment.from_ogg(ogg_file)
    sound.export(wav_file, format="wav")

    # Распознавание речи
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_file) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language="ru-RU")

            await talking(message, text)
        except sr.UnknownValueError:
            await message.reply("Не удалось распознать речь 😕")
        except Exception as e:
            await message.reply(f"Ошибка: {e}")

    # Удаляем временные файлы
    os.remove(ogg_file)
    os.remove(wav_file)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
