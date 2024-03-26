#!/usr/bin/env python

"""
Usage:
    ade-feed-url [options] <for_username> [<login_as_username>] [<password>]

If <password> is omitted, the password will be calculated by running `rbw get inp-toulouse.fr`.
See https://github.com/doy/rbw to learn more about rbw, a Bitwarden (https://bitwarden.com) CLI.

Options:
    -v, --verbose       Show information about steps being executed
"""

import subprocess
from datetime import date
from time import sleep

from docopt import docopt
from filelock import FileLock
from helium import (
    S,
    click,
    get_driver,
    go_to,
    kill_browser,
    start_chrome,
    wait_until,
    write,
)
from pyvirtualdisplay import Display
from selenium.webdriver.chrome.options import Options

helium_lock = FileLock(".helium_lock", timeout=60 * 60)


def login_to_ade(username: str, password: str = "", verbose=False, logger=print):
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    password = password or subprocess.run(
        ["rbw", "get", "inp-toulouse.fr"], capture_output=True
    ).stdout.decode("utf-8")
    if verbose:
        logger(f"Logging in as {username}…")
    start_chrome(
        "http://planete.inp-toulouse.fr", headless=False, options=chrome_options
    )

    click("S'identifier")
    write(username, into="Username")
    write(password, into="Password")
    click("Login")
    sleep(3)
    if verbose:
        logger("Opening ADE…")
    go_to("https://edt.inp-toulouse.fr/direct/myplanning.jsp")
    sleep(6)


def go_to_user_planning(username: str, verbose=False, logger=print):
    if verbose:
        logger("Opening advanced search")
    button_selector = "button[aria-describedby=x-auto-7]"
    if verbose:
        logger(f"Waiting for {button_selector!r} to exist on page...")
    wait_until(S(button_selector).exists)
    if verbose:
        logger(f"Clicking on {button_selector!r}")
    get_driver().execute_script(f"document.querySelector({button_selector!r}).click()")
    sleep(3)
    if verbose:
        logger("Selecting uid filter mode")
    click("uid")
    click("Ok")
    if verbose:
        logger(f"Searching for uid={username}")
    write(username, into="Code X contains")
    click("Ok")
    sleep(5)


def get_resource_id(verbose=False, logger=print) -> str:
    if verbose:
        logger("Scraping resource id")
    selector = '.x-grid3-row-selected[id^="Direct Planning Tree"] .x-tree3-node[id^="Direct Planning Tree"]'
    if verbose:
        logger(f"Waiting for {selector!r} to exist on page")
    wait_until(S(selector).exists)
    if verbose:
        logger(f"Getting id attribute of {selector!r}")
    resource_id = (
        get_driver()
        .execute_script(
            f"return document.querySelector({selector!r}).getAttribute('id').replace('Direct Planning Tree_')"
        )
        .replace("undefined", "")
    )
    return resource_id


def school_year_start(_date: date) -> int:
    year = _date.year
    month = _date.month
    day = _date.day
    if month < 9 or (month == 9 and day < 1):
        return year - 1
    return year


def make_ical_url(resource_id: str, verbose=False, logger=print):
    if verbose:
        logger(f"Constructing iCal feed URL for resource {resource_id}")

    startOfSchoolYear = f"{school_year_start(date.today())}-09-01"
    endOfSchoolYear = f"{school_year_start(date.today())+1}-08-20"

    return f"https://edt.inp-toulouse.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?resources={resource_id}&projectId=65&calType=ical&firstDate={startOfSchoolYear}&lastDate={endOfSchoolYear}"


def main(
    login_as_username: str,
    for_username: str,
    password: str = "",
    verbose=False,
    logger=print,
):
    with helium_lock:
        logger("Acquired helium lock")
        display = Display(visible=0, size=(800, 600))
        display.start()
        login_to_ade(login_as_username, password, verbose, logger)
        go_to_user_planning(for_username, verbose, logger)
        resource_id = get_resource_id(verbose, logger)
        ical_url = make_ical_url(resource_id, verbose, logger)
        kill_browser()
        display.stop()
    logger("Released helium lock")
    logger(ical_url)
    return ical_url


def run(options):
    options = options or docopt(__doc__)
    for_username = options["<for_username>"]
    login_as_username = options["<login_as_username>"] or for_username
    password = options["<password>"]
    verbose = options["--verbose"]

    return main(login_as_username, for_username, password, verbose)


if __name__ == "__main__":
    run()
