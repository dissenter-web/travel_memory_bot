import re
from datetime import date
from pathlib import Path

from app.models import MemoryMetadata


FILENAME_PATTERN = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})"
    r"__(?P<trip>[a-z0-9]+(?:-[a-z0-9]+)*)"
    r"__(?P<place>[a-z0-9]+(?:-[a-z0-9]+)*)"
    r"__(?P<sequence>\d{3})$"
)


class InvalidPhotoFilenameError(ValueError):
    pass


def parse_photo_filename(photo_path: Path) -> MemoryMetadata:
    match = FILENAME_PATTERN.fullmatch(photo_path.stem)
    if match is None:
        raise InvalidPhotoFilenameError(
            "Invalid photo filename "
            f"{photo_path.name!r}. Expected format: "
            "YYYY-MM-DD__trip-name__place-name__001.jpg"
        )

    try:
        taken_on = date.fromisoformat(match.group("date"))
    except ValueError as exc:
        raise InvalidPhotoFilenameError(
            f"Invalid date in photo filename {photo_path.name!r}"
        ) from exc

    return MemoryMetadata(
        taken_on=taken_on,
        trip_slug=match.group("trip"),
        place_slug=match.group("place"),
        sequence=int(match.group("sequence")),
    )
