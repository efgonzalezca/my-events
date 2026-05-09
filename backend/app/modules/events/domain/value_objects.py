from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class EventStatus(str, Enum):
    draft = "draft"
    published = "published"
    cancelled = "cancelled"


@dataclass(frozen=True)
class DateRange:
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.end <= self.start:
            raise ValueError("end must be after start")

    def overlaps(self, other: "DateRange") -> bool:
        return self.start < other.end and other.start < self.end

    def contains(self, other: "DateRange") -> bool:
        return self.start <= other.start and other.end <= self.end
