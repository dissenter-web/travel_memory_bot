from html import escape

from app.models import Memory


MONTHS_RU = {
    1: "января", 2: "февраля", 3: "марта", 4: "апреля",
    5: "мая", 6: "июня", 7: "июля", 8: "августа",
    9: "сентября", 10: "октября", 11: "ноября", 12: "декабря",
}


def _humanize_slug(value: str) -> str:
    return value.replace("-", " ").title()


def _format_date(memory: Memory) -> str:
    taken_on = memory.metadata.taken_on
    return f"{taken_on.day} {MONTHS_RU[taken_on.month]} {taken_on.year} года"


def _build_hashtag(value: str) -> str:
    return "#" + "".join(part.capitalize() for part in value.split("-"))


def format_memory_caption(memory: Memory, phrase: str) -> str:
    place = escape(_humanize_slug(memory.metadata.place_slug))
    trip = escape(_humanize_slug(memory.metadata.trip_slug))
    taken_on = escape(_format_date(memory))
    trip_hashtag = escape(_build_hashtag(memory.metadata.trip_slug))
    safe_phrase = escape(phrase)

    return "\n".join([
        f"📍 <b>{place}</b>",
        f"📅 {taken_on}",
        f"🧳 {trip}",
        "",
        safe_phrase,
        "",
        f"{trip_hashtag} #НашиПутешествия",
    ])
