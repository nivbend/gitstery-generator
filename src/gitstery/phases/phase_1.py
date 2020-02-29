from itertools import chain
from random import choice
from click import echo, progressbar
from ..defines import (DATA_DIR, DATE_END, DATE_REPORT, DATE_REPORT_WEEK_START, POLICE_BRANCH,
    DATE_REPORT_WEEK_END)
from ..people import MAIN_DETECTIVE, OTHER_DETECTIVES
from ..fillers import random_paragraphs, random_ids, random_datetimes
from ..git_utils import git_commit, in_branch

@in_branch(POLICE_BRANCH)
def build_phase_1(repo):
    """First phase requiring some history lookup skills.

    Finding specific commits in a long history is a common task. It helps answering questions such
    as "when was the last time we bumped the version?", "what changes happened on the branch since
    we last deployed to production?" or "who was the last person to change this file and why?"

    This first step towards the solution will make the player pin down a specific commit in a sea
    of unrelevant "fluff" commits. Leading them to use `git log` with some extra flags.
    """
    all_detectives = OTHER_DETECTIVES + [MAIN_DETECTIVE, ]
    report_ids = random_ids()

    # Commit some reports before the main one, making sure the ones on the same week aren't
    # from the main detective.
    reports_before = 84
    dates = chain(
        zip((choice(all_detectives) for _ in range(reports_before - 1)),
            random_datetimes(reports_before - 1, DATE_REPORT_WEEK_START, hour_max=23)),
        zip((choice(OTHER_DETECTIVES) for _ in range(1)),
            random_datetimes(1, DATE_REPORT_WEEK_START, DATE_REPORT, hour_max=23)))
    with progressbar(dates, length=reports_before, label='Comitting scene report before') as bar:
        for (detective, date) in bar:
            git_commit(repo, detective, date,
                f'Crime scene report #{next(report_ids)}',
                random_paragraphs())

    echo('Committing the main crime scene report')
    main_report_path = DATA_DIR / 'main-report.txt'
    main_report = main_report_path.read_text()
    git_commit(repo, MAIN_DETECTIVE, DATE_REPORT,
        f'Crime scene report #{next(report_ids)}',
        main_report)

    # Commit some reports after the main one, making sure the ones on the same week aren't
    # from the main detective.
    reports_after = 92
    dates = chain(
        zip((choice(OTHER_DETECTIVES) for _ in range(2)),
            random_datetimes(2, DATE_REPORT, DATE_REPORT_WEEK_END, hour_max=23)),
        zip((choice(all_detectives) for _ in range(reports_after - 2)),
            random_datetimes(reports_after - 2, DATE_REPORT_WEEK_END, DATE_END, hour_max=23)))
    with progressbar(dates, length=reports_after, label='Comitting scene report after') as bar:
        for (detective, date) in bar:
            git_commit(repo, detective, date,
                f'Crime scene report #{next(report_ids)}',
                random_paragraphs())
