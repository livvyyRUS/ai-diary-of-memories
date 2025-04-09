from transformers import pipeline


async def translate_text(
        text: str,
        source_lang: str = "en",
        target_lang: str = "ru"
) -> str | None:
    # Проверка поддерживаемых языковых пар
    supported_pairs = [("en", "ru"), ("ru", "en")]

    if (source_lang, target_lang) not in supported_pairs:
        raise ValueError(f"Unsupported language pair. Only {supported_pairs} are supported.")

    print(f"Перевод с {source_lang} на {target_lang}...")

    try:
        # Динамический выбор специализированной модели
        model_name = f"Helsinki-NLP/opus-mt-{source_lang}-{target_lang}"
        translator = pipeline("translation", model=model_name)

        # Выполнение перевода
        result = translator(text)
        return result[0]["translation_text"]

    except Exception as e:
        print(f"Ошибка перевода: {e}")
        return None
