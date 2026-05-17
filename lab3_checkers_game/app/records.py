import json
import os

RECORDS_PATH = "records.json"


class RecordManager:
    """Управляет сохранением и загрузкой накопительного рейтинга игроков."""

    def __init__(self):
        self.records = {}
        self.load()

    def load(self):
        if os.path.exists(RECORDS_PATH):
            try:
                with open(RECORDS_PATH, "r", encoding="utf-8") as f:
                    self.records = json.load(f)
            except Exception:
                self.records = {}

    def save(self):
        with open(RECORDS_PATH, "w", encoding="utf-8") as f:
            json.dump(self.records, f, indent=4, ensure_ascii=False)

    def update_record(self, name: str, score_delta: int):
        """Добавляет или вычитает очки из профиля игрока."""
        if not name or name.strip() == "":
            return

        if name not in self.records:
            self.records[name] = 0

        self.records[name] += score_delta
        self.save()

    def get_top(self, limit=7) -> list:
        """Возвращает топ N игроков, отсортированных по убыванию очков."""
        sorted_records = sorted(self.records.items(), key=lambda item: item[1], reverse=True)
        return sorted_records[:limit]