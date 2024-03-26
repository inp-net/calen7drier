#!/usr/bin/env python
from datetime import datetime
from os import getenv
from typing import Any, Iterable, NamedTuple

import requests
from filelock import FileLock
from ics import Calendar
from pytz import timezone

from .main import main as main_main

REQUESTS_LOCK = FileLock(".requests_lock")


class ADEEvent(NamedTuple):
    starts_at: datetime
    ends_at: datetime
    apogee_code: str
    type: str
    group: str
    title: str

    def serialize(self):
        return self._asdict() | {
            "starts_at": self.starts_at.isoformat(),
            "ends_at": self.ends_at.isoformat(),
        }


def parse_feed(url: str, logger=print) -> Iterable[ADEEvent]:
    with REQUESTS_LOCK:
        logger("Acquired requests lock")
        calendar = Calendar(requests.get(url).text)
    logger("Released requests lock")

    for event in calendar.events:
        event.name = (
            event.name.replace("- ", " - ").replace(" -", " - ").replace("  ", " ")
        )
        if " - " not in event.name:
            continue
        [apogee_code, rest] = event.name.split(" - ", 1)

        type = ""
        group = ""
        if rest.count(" - ") >= 2:
            [type, group, rest] = rest.split(" - ", 2)

        if type.strip() == "Examens":
            type = "Examen"

        yield ADEEvent(
            starts_at=event.begin.datetime.astimezone(tz=timezone("Europe/Paris")),
            ends_at=event.end.datetime.astimezone(tz=timezone("Europe/Paris")),
            apogee_code=apogee_code.strip(),
            title=rest.strip(),
            type=type.strip(),
            group=group.strip(),
        )


def feed_as_json(ical_url: str, logger=print) -> list[dict[str, Any]]:
    feed = list(parse_feed(ical_url, logger))

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

    return [with_camel_case_keys(event._asdict()) for event in feed]


def main(username: str):
    ical_url = main_main(
        for_username=username,
        login_as_username=getenv("LOGIN_AS", ""),
        password=getenv("PASSWORD", ""),
        verbose=True,
    )

    feed = list(parse_feed(ical_url))

    for event in feed:
        if event.type in {"Examen", "BE"}:
            print(
                f'{event.type:6} for {event.apogee_code} "{event.title}"'.ljust(50)
                + f"on {event.starts_at:%d %b %Y at %H:%M}, lasting {event.ends_at - event.starts_at} (for group {event.group})"
            )
