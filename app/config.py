from dataclasses import dataclass
from datetime import time
from os import getenv
from pathlib import Path
from zoneinfo import ZoneInfo


def _required(name: str) -> str:
    value = getenv(name)
    if not value:
        raise RuntimeError(f"Environment variable {name} is required")
    return value


def _parse_user_ids(raw: str) -> frozenset[int]:
    try:
        ids = frozenset(int(item.strip()) for item in raw.split(",") if item.strip())
    except ValueError as exc:
        raise RuntimeError("ALLOWED_USER_IDS must contain comma-separated integers") from exc

    if not ids:
        raise RuntimeError("ALLOWED_USER_IDS must contain at least one Telegram user ID")
    return ids


def _parse_send_time(raw: str, timezone: ZoneInfo) -> time:
    try:
        hours, minutes = map(int, raw.split(":"))
        return time(hour=hours, minute=minutes, tzinfo=timezone)
    except (ValueError, TypeError) as exc:
        raise RuntimeError("SEND_TIME must use HH:MM format, for example 09:00") from exc


@dataclass(frozen=True, slots=True)
class Settings:
    bot_token: str
    allowed_user_ids: frozenset[int]
    admin_user_id: int
    timezone: ZoneInfo
    send_time: time
    data_dir: Path
    photos_dir: Path
    phrases_file: Path
    database_file: Path


def load_settings() -> Settings:
    data_dir = Path(getenv("DATA_DIR", "/app/data"))
    timezone = ZoneInfo(getenv("TIMEZONE", "Europe/Moscow"))
    allowed_user_ids = _parse_user_ids(_required("ALLOWED_USER_IDS"))
    admin_user_id = int(getenv("ADMIN_USER_ID", str(next(iter(allowed_user_ids)))))

    if admin_user_id not in allowed_user_ids:
        raise RuntimeError("ADMIN_USER_ID must also be present in ALLOWED_USER_IDS")

    return Settings(
        bot_token=_required("BOT_TOKEN"),
        allowed_user_ids=allowed_user_ids,
        admin_user_id=admin_user_id,
        timezone=timezone,
        send_time=_parse_send_time(getenv("SEND_TIME", "09:00"), timezone),
        data_dir=data_dir,
        photos_dir=data_dir / "photos",
        phrases_file=data_dir / "phrases.json",
        database_file=data_dir / "bot.sqlite3",
    )
