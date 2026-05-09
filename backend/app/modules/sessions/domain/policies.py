from app.modules.events.domain.value_objects import DateRange


class SchedulePolicy:
    @staticmethod
    def fits_in(session_range: DateRange, event_range: DateRange) -> bool:
        return event_range.contains(session_range)

    @staticmethod
    def overlaps_with(
        session_range: DateRange, others: list[DateRange]
    ) -> bool:
        return any(session_range.overlaps(o) for o in others)