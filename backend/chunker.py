import re
from typing import List


def normalize_text(text: str) -> str:
    text = text.replace("\x00", " ")

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()


def split_into_chunks(
    text: str,
    target_words: int = 400,
    overlap_words: int = 60,
) -> List[str]:

    text = normalize_text(text)

    if not text:
        return []

    words = text.split()

    if len(words) <= target_words:
        return [text]

    chunks = []

    start = 0

    while start < len(words):

        end = min(
            start + target_words,
            len(words),
        )

        chunk = " ".join(words[start:end]).strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap_words

    return chunks