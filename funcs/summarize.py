from transformers import pipeline


def summarizing(text: str) -> str:
    """
    Функция принимает строку с сообщениями, разделёнными тегами вида:
    '#NEW MESSAGE FROM USER' и '#NEW MESSAGE FROM ME'
    и возвращает суммаризацию, описывающую день пользователя.
    """
    # Разбиваем входной текст по строкам
    lines = text.splitlines()

    # Собираем все сообщения, игнорируя строки с тегами
    messages = []
    for line in lines:
        stripped = line.strip()
        # Пропускаем строки, начинающиеся с #NEW MESSAGE
        if "#NEW MESSAGE FROM ME" in stripped:
            stripped = stripped.replace("#NEW MESSAGE FROM ME", "")
        if "#NEW MESSAGE FROM USER" in stripped:
            stripped = stripped.replace("#NEW MESSAGE FROM USER", "")
        # Если строка не пустая, добавляем её в список
        messages.append(stripped)

    # Объединяем сообщения в один текст для суммаризации
    full_text = " ".join(messages)

    # Инициализируем пайплайн суммаризации
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    # Выполняем суммаризацию с указанием желаемой длины результата
    summary = summarizer(full_text, max_length=150, min_length=50, do_sample=False)

    return summary[0]['summary_text']
