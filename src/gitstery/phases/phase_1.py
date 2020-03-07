from random import choice
from click import echo, progressbar
from ..defines import (DATA_DIR, DATE_END, DATE_REPORT, DATE_REPORT_WEEK_START, POLICE_BRANCH,
    DATE_REPORT_WEEK_END)
from ..people import MAIN_DETECTIVE, OTHER_DETECTIVES
from ..fillers import random_paragraphs, random_ids, random_datetimes
from ..git_utils import git_commit, in_branch

@in_branch(POLICE_BRANCH)
def build_phase_1(repo):
    """First phase requiring some history lookup skills."""
    all_detectives = OTHER_DETECTIVES + [MAIN_DETECTIVE, ]
    report_ids = random_ids()

    # Commit some reports before the main one.
    reports_before = 84
    dates = zip((choice(all_detectives) for _ in range(reports_before)),
            random_datetimes(reports_before, DATE_REPORT_WEEK_START, hour_max=23))
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

    # Commit some reports after the main one.
    reports_after = 92
    dates = zip((choice(all_detectives) for _ in range(reports_after)),
            random_datetimes(reports_after, DATE_REPORT_WEEK_END, DATE_END, hour_max=23))
    with progressbar(dates, length=reports_after, label='Comitting scene report after') as bar:
        for (detective, date) in bar:
            git_commit(repo, detective, date,
                f'Crime scene report #{next(report_ids)}',
                random_paragraphs())
