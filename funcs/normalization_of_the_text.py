def normalization_of_the_text(_text: str) -> str:
    x = _text.find('</think>')
    return _text[x + 10:]
