#!/usr/bin/env python
from pathlib import Path
import requests
import json
from main import main
from ics import Calendar
from typing import NamedTuple, Iterable, Any
from datetime import datetime
from pytz import timezone


class ADEEvent(NamedTuple):
    starts_at: datetime
    ends_at: datetime
    apogee_code: str
    type: str
    group: str
    title: str


def parse_feed(url: str) -> Iterable[ADEEvent]:
    calendar = Calendar(requests.get(url).text)

    for event in calendar.events:
        if " - " not in event.name:
            print(f"Skipping event {event.name}")
            continue
        [apogee_code, rest] = event.name.split(" - ", 1)

        type = ""
        group = ""
        if rest.count(" - ") >= 2:
            [type, group, rest] = rest.split(" - ", 2)

        if type == "Examens":
            type = "Examen"

        yield ADEEvent(
            starts_at=event.begin.datetime.astimezone(tz=timezone("Europe/Paris")),
            ends_at=event.end.datetime.astimezone(tz=timezone("Europe/Paris")),
            apogee_code=apogee_code,
            title=rest,
            type=type,
            group=group,
        )


if __name__ == "__main__":
    """
    ical_url = main({
        '<for_username>': input('for: '),
        '<login_as_username>': 'elebihan',
        '<password>': None,
        '--verbose': True
    })
    """
    ical_url = "https://edt.inp-toulouse.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?resources=3018&projectId=65&calType=ical&firstDate=2023-09-01&lastDate=2024-08-20"

    feed = list(parse_feed(ical_url))

    def with_camel_case_keys(o: dict[str, Any]) -> dict[str, Any]:
        def transform_key(key: str) -> str:
            [first_word, *other_words] = key.split("_")
            return first_word.lower() + "".join(
                word.capitalize() for word in other_words
            )

        return {
            transform_key(key): with_camel_case_keys(value)
            if isinstance(value, dict)
            else value
            for key, value in o.items()
        }

    Path("feed.json").write_text(
        json.dumps(
            [with_camel_case_keys(event._asdict()) for event in feed],
            indent=4,
            default=lambda x: x.isoformat(),
            ensure_ascii=False,
        )
    )

    for event in feed:
        if event.type in {"Examen", "BE"}:
            print(
                f'{event.type:6} for {event.apogee_code} "{event.title}"'.ljust(50)
                + f"on {event.starts_at:%d %b %Y at %H:%M}, lasting {event.ends_at - event.starts_at} (for group {event.group})"
            )
