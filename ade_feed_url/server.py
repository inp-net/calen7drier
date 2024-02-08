import json
from contextlib import contextmanager
from datetime import date, datetime
from http.client import UNAUTHORIZED
from os import getenv
from pathlib import Path
from typing import Any, Literal, NamedTuple, Optional

import requests
import typed_dotenv
from churros.client import ChurrosClient
from filelock import FileLock
from flask import (Flask, make_response, redirect, render_template, request,
                   send_from_directory)
from pydantic import BaseModel
from pytz import timezone
from rich.console import Console

from .main import main, school_year_start
from .parse_feed import feed_as_json, parse_feed


class Environment(BaseModel):
    CHURROS_CLIENT_ID: str
    CHURROS_CLIENT_SECRET: str
    ORIGIN: str
    LOGIN_AS: str
    PASSWORD: str


dotenv_file = Path(__file__).parent.parent / ".env"
env: Environment

if dotenv_file.exists():
    env = typed_dotenv.load_into(Environment, filename=dotenv_file)
else:
    env = Environment(
        CHURROS_CLIENT_ID=getenv("CHURROS_CLIENT_ID"),
        CHURROS_CLIENT_SECRET=getenv("CHURROS_CLIENT_SECRET"),
        ORIGIN=getenv("ORIGIN"),
        LOGIN_AS=getenv("LOGIN_AS"),
        PASSWORD=getenv("PASSWORD"),
    )

console = Console()


def log(uid: str | None, area: str, message: str, error=False):
    c = lambda color: "red" if error else color
    cyan = c("cyan")
    magenta = c("magenta")
    console.print(
        f"\\[[{cyan} bold]{area}[/{cyan} bold]] ".ljust(40)
        + (
            f"[{magenta}]@{uid}[/{magenta}] " if uid else f"[{magenta}][/{magenta}]"
        ).ljust(30)
        + message.replace("[", "\\["),
        soft_wrap=False,
        crop=False,
    )


def logger_of(uid: str | None, area: str):
    return lambda *args: log(uid, area, " ".join(args))


app = Flask("ade_feed_url", root_path=Path(__file__).parent)
# app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

CACHE_LOCATION = Path("cache/cache.json")
CACHE_LOCK = FileLock("cache/.lock")

EXAM_TYPES = {"be", "exam", "examen", "partiel", "oral"}


def revive_datestrings(o: dict[str, Any]):
    return {
        k: datetime.fromisoformat(v) if k == "last_modified" else v
        for k, v in o.items()
    }


@contextmanager
def open_cache(mode: str, uid: str):
    # TODO don't acquire lock if reading?
    with CACHE_LOCK:
        log(uid, "lock:acquire", "Acquired cache lockfile")
        if not CACHE_LOCATION.parent.exists() or not CACHE_LOCATION.exists():
            CACHE_LOCATION.parent.mkdir(exist_ok=True)
            CACHE_LOCATION.write_text("{}")
        if CACHE_LOCATION.lstat().st_size == 0:
            CACHE_LOCATION.write_text("{}")
        with open(CACHE_LOCATION, mode) as f:
            yield f
    log(uid, "lock:release", "Released cache lockfile")


@contextmanager
def read_cache(uid: str):
    log(uid, "cache:read", f"Reading cache at {CACHE_LOCATION}")
    with open_cache("r", uid) as f:
        cache: dict[str, CacheEntry] = {
            uid: CacheEntry(**revive_datestrings(entry))  # type: ignore
            for uid, entry in json.load(f).items()
        }
        log(uid, "cache:read", f"Read cache ({len(cache)} entries)")
        yield cache


class CacheEntry(NamedTuple):
    url: str
    last_modified: datetime


class Cache:
    def __init__(self, uid: str) -> None:
        log(uid, "cache:open", f"Opening cache at {CACHE_LOCATION}")

    def _write(self, cache: dict[str, CacheEntry], uid: str):
        with open_cache("w", uid) as f:
            f.write(
                json.dumps(
                    {uid: entry._asdict() for uid, entry in cache.items()},
                    default=lambda o: o.isoformat() if isinstance(o, datetime) else o,
                )
            )

    def invalidate(self, uid: str):
        log(uid, "cache:invalidate", f"Invalidating {uid} from cache")
        with read_cache(uid) as cache:
            if uid in cache:
                del cache[uid]
        self._write(cache, uid)

    def get(self, uid: str) -> Optional[str]:
        log(uid, "cache:query", f"Querying {uid} in cache")
        with read_cache(uid) as cache:
            entry = cache.get(uid)
            if not entry:
                return None

            log(uid, "cache:found", f"Cache entry is {entry}")
            this_school_year = school_year_start(date.today())
            cache_school_year = school_year_start(entry.last_modified.date())

            if this_school_year != cache_school_year:
                self.invalidate(uid)
                return None

            return entry.url

    def add(self, uid: str, url: str):
        log(uid, "cache:save", f"Adding {uid}={url!r} to cache")
        with read_cache(uid) as cache:
            cache[uid] = CacheEntry(url, datetime.now())
        self._write(cache, uid)


def get_feed_url(uid: str) -> str:
    cache = Cache(uid)

    if cached := cache.get(uid):
        return cached

    log(uid, "main", f"{uid} not in cache, scraping")
    log(
        uid,
        "env",
        f"using LOGIN_AS={env.LOGIN_AS} PASSWORD={len(env.PASSWORD) * '*'!r}",
    )

    url = main(
        env.LOGIN_AS,
        uid,
        env.PASSWORD,
        True,
        lambda *args: log(uid, "ade", " ".join(args)),
    )
    log(uid, "main", f"Got {url}")

    cache.add(uid, url)
    return url


def graphql(query: str, token: str | None = None) -> Any:
    return requests.post(
        "https://churros.inpt.fr/graphql",
        json={"query": query},
        headers={"Authorization": f"Bearer {token}"} if token else {},
    ).json()


def can_access_calendar(churros_token: str) -> Literal[False] | dict[str, Any]:
    try:
        if not churros_token:
            return False
        else:
            data = graphql(
                "query {me {schoolUid, major { schools { uid } }}}", churros_token
            )

            uid = data["data"]["me"]["schoolUid"]
            schools = [
                school["uid"] for school in data["data"]["me"]["major"]["schools"]
            ]
            valid = any(school == "n7" for school in schools)

            if valid:
                log(uid, "auth", "passed")
                return data["data"]["me"]
            else:
                log(
                    uid,
                    "auth",
                    f"denied: n7 not in {', '.join(schools)}. response: {data}",
                )
                return False
    except KeyError:
        log(None, "auth", f"reject because of GraphQL error {data!r}")
    except Exception as e:
        log(None, "auth", f"reject because of error {e!r}")
        return False


def unauthorized_error():
    if not can_access_calendar(
        request.cookies.get("token")
        or request.args.get("token")
        or request.headers.get("Authorization", "").replace("Bearer ", "")
    ):
        return (
            "unauthorized. pass a Churros token as a GET parameter or a cookie, named 'token'",
            UNAUTHORIZED,
        )
    return None


@app.route("/favicon.ico")
def favicon():
    return "", 404


@app.route("/assets/<path:path>")
def assets(path):
    return send_from_directory("assets", path)


@app.route("/oauth/callback")
def oauth_callback():
    code = request.args.get("code")
    state = request.args.get("state")

    if not code or not state:
        return "Unauthorized", UNAUTHORIZED

    churros = ChurrosClient(
        client_id=env.CHURROS_CLIENT_ID,
        client_secret=env.CHURROS_CLIENT_SECRET,
        redirect_uri=f"{env.ORIGIN}/oauth/callback",
    )

    churros.state = request.cookies.get("csrf_state")
    token = churros.get_token(code, state)

    response = redirect("/")
    response.set_cookie("token", token, secure=True, httponly=True)
    response.set_cookie("csrf_state", "", expires=0)
    return response


@app.route("/logout")
def logout():
    token = request.cookies.get("token")
    if not token:
        return "ok", 200

    graphql("mutation { logout }", token)
    response = make_response()
    response.set_cookie("token", "", expires=0)
    return response


@app.route("/")
def home():
    if user := can_access_calendar(request.cookies.get("token")):
        return render_template("index.html.j2", school_uid=user["schoolUid"])
    else:
        churros = ChurrosClient(
            client_id=env.CHURROS_CLIENT_ID,
            client_secret=env.CHURROS_CLIENT_SECRET,
            redirect_uri=f"{env.ORIGIN}/oauth/callback",
        )
        churros.generate_state()

        response = redirect(churros.authorization_url)
        response.set_cookie("csrf_state", churros.state, secure=True, httponly=True)
        return response


@app.route("/cache")
def cache_status():
    with read_cache("(cache_status)") as cache:
        return f"{len(cache)} entries", 200


@app.route("/<uid>")
def redirect_to_feed(uid: str):
    if err := unauthorized_error():
        return err
    try:
        url = get_feed_url(uid)
    except Exception as e:
        if str(e) == "Not found":
            return "not found", 404
        log(uid, "redirect", f"Failed with exception {str(e)}", True)
        return "internal error", 500
    return redirect(url)


@app.route("/<uid>/goofy")
def goofy_feed(uid: str):
    if err := unauthorized_error():
        return err
    try:
        url = get_feed_url(uid)
    except Exception as e:
        if str(e) == "Not found":
            return "not found", 404
        log(uid, "redirect", f"Failed with exception {str(e)}", True)
        return "internal error", 500
    response = requests.get(url)
    content = (
        response.text.replace("Fasson Julien", "Le J (c'est le S)")
        .replace("Riad Dhaou", "Complètement Daou")
        .replace("Emmanuel Chaput", "Manux")
    )
    return content, {"Content-Type": "text/calendar;charset=UTF-8"}


@app.route("/<uid>/url")
def show_feed_url(uid: str):
    if err := unauthorized_error():
        return err
    try:
        url = get_feed_url(uid)
    except Exception as e:
        if str(e) == "Not found":
            return "not found", 404
        log(uid, "redirect", f"Failed with exception {e}", True)
        return "internal error", 500
    return url, 200


@app.route("/<uid>/invalidate")
def invalidate(uid: str):
    cache = Cache(uid)
    cache.invalidate(uid)
    return "ok", 200


@app.route("/<uid>/feed.json")
def json_feed(uid: str):
    try:
        url = get_feed_url(uid)
        return (
            feed_as_json(
                url, logger=lambda *args: log(uid, "json_feed", " ".join(args))
            ),
            200,
        )
    except Exception as e:
        if str(e) == "Not found":
            return "not found", 404
        log(uid, "json_feed", f"Failed with exception {e}", True)
        return "internal error", 500


@app.route("/<uid>/<subject_code>/next-exam/")
def next_exam(uid: str, subject_code: str):
    try:
        url = get_feed_url(uid)
        events_of_subject = [
            event
            for event in parse_feed(url, logger=logger_of(uid, "next_exam"))
            if event.apogee_code.lower() == subject_code.lower()
            and event.type.lower().strip() in EXAM_TYPES
        ]
        events_of_subject.sort(key=lambda event: event.starts_at)
        if not len(events_of_subject):
            return "subject not found or no exams in subject", 404
        event = events_of_subject[0]
        return event.serialize()
    except Exception as e:
        if str(e) == "Not found":
            return "user not found", 404
        log(uid, "next_exam", f"Failed with exception {e}", True)
        return "internal error", 500


@app.route("/<uid>/next-exams")
def next_exams(uid: str):
    if err := unauthorized_error():
        return err
    try:
        url = get_feed_url(uid)
        exams = [
            event
            for event in parse_feed(url, logger=logger_of(uid, "next_exams"))
            if event.type.lower().strip() in EXAM_TYPES
        ]

        def closest_of_subject(subject_code: str):
            return sorted(
                filter(
                    lambda event: event.apogee_code.lower() == subject_code.lower(),
                    exams,
                ),
                key=lambda event: (
                    event.starts_at.astimezone(timezone("Europe/Paris"))
                    - datetime.now(timezone("Europe/Paris"))
                ),
            )[0]

        apogee_codes = {e.apogee_code for e in exams}

        if not len(exams):
            return "user not found or no exams for user", 404

        return {code: closest_of_subject(code).serialize() for code in apogee_codes}
    except Exception as e:
        if str(e) == "Not found":
            return "user not found", 404
        log(uid, "next_exams", f"Failed with exception {e}", True)
        return "internal error", 500


@app.route("/<uid>/subjects")
def subjects(uid: str):
    try:
        url = get_feed_url(uid)
        feed = parse_feed(url, logger=logger_of(uid, "subjects"))
        return {e.apogee_code: e.title for e in feed if e.apogee_code.startswith("N")}
    except Exception as e:
        if str(e) == "Not found":
            return "user not found", 404
        log(uid, "subjects", f"Failed with exception {e!r}", True)
        return "internal error", 500
