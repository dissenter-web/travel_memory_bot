import json
import random
from pathlib import Path


DEFAULT_PHRASE = "Спасибо, что мы создаём эти воспоминания вместе ❤️"


class PhraseRepository:
    def __init__(self, phrases_file: Path) -> None:
        self.phrases_file = phrases_file

    def get_random_phrase(self) -> str:
        if not self.phrases_file.exists():
            return DEFAULT_PHRASE

        with self.phrases_file.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise RuntimeError("phrases.json must contain a JSON array")

        phrases = [str(item).strip() for item in data if str(item).strip()]
        if not phrases:
            return DEFAULT_PHRASE

        return random.choice(phrases)
