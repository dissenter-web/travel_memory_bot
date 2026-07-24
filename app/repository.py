import logging
import sqlite3
from pathlib import Path

from app.filename_parser import InvalidPhotoFilenameError, parse_photo_filename
from app.models import Memory


logger = logging.getLogger(__name__)
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


class MemoryRepository:
    def __init__(self, photos_dir: Path, database_file: Path) -> None:
        self.photos_dir = photos_dir
        self.database_file = database_file

    def initialize(self) -> None:
        self.photos_dir.mkdir(parents=True, exist_ok=True)
        self.database_file.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.database_file) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sent_memories (
                    memory_key TEXT PRIMARY KEY,
                    sent_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def load_memories(self) -> list[Memory]:
        memories: list[Memory] = []

        for photo_path in sorted(self.photos_dir.iterdir()):
            if not photo_path.is_file() or photo_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            try:
                metadata = parse_photo_filename(photo_path)
            except InvalidPhotoFilenameError:
                logger.exception("Skipping photo with invalid filename")
                continue

            memories.append(
                Memory(
                    key=photo_path.name,
                    photo_path=photo_path,
                    metadata=metadata,
                )
            )

        return memories

    def get_sent_keys(self) -> set[str]:
        with sqlite3.connect(self.database_file) as connection:
            rows = connection.execute("SELECT memory_key FROM sent_memories").fetchall()
        return {row[0] for row in rows}

    def mark_as_sent(self, memory_key: str) -> None:
        with sqlite3.connect(self.database_file) as connection:
            connection.execute(
                "INSERT OR REPLACE INTO sent_memories(memory_key, sent_at) VALUES (?, CURRENT_TIMESTAMP)",
                (memory_key,),
            )

    def reset_history(self) -> None:
        with sqlite3.connect(self.database_file) as connection:
            connection.execute("DELETE FROM sent_memories")
