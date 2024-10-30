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

from docopt import docopt
from .env import env

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

    return f"https://edt.inp-toulouse.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?resources={resource_id}&projectId={env.ADE_PROJECT_ID}&calType=ical&firstDate={startOfSchoolYear}&lastDate={endOfSchoolYear}"


def main(
    login_as_username: str,
    for_username: str,
    password: str = "",
    verbose=False,
    logger=print,
):
    resource_id = int(subprocess.run(
        ["ade-bash-client/main.sh", login_as_username, for_username], input=password.encode("utf-8"), capture_output=True
    ).stdout.decode("utf-8"))
    return make_ical_url(resource_id)



def run(options = None):
    options = options or docopt(__doc__)
    for_username = options["<for_username>"]
    login_as_username = options["<login_as_username>"] or for_username
    password = options["<password>"] or env.PASSWORD
    verbose = options["--verbose"]

    return main(login_as_username, for_username, password, verbose)


if __name__ == "__main__":
    run()
