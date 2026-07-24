from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True, slots=True)
class MemoryMetadata:
    taken_on: date
    trip_slug: str
    place_slug: str
    sequence: int


@dataclass(frozen=True, slots=True)
class Memory:
    key: str
    photo_path: Path
    metadata: MemoryMetadata
