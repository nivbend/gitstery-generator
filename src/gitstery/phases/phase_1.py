from itertools import chain
from random import choice
from click import echo, progressbar
from inflect import engine
from ..defines import (DATA_DIR, DATE_END, ACCESS_POINT_OF_INTEREST, DATE_MURDER, DATE_REPORT,
    DATE_REPORT_WEEK_START, DATE_REPORT_WEEK_END, POLICE_BRANCH)
from ..people import MAIN_DETECTIVE, OTHER_DETECTIVES
from ..fillers import random_paragraphs, random_ids, random_datetime, random_datetimes
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
    inflect = engine()
    days_since_murder = DATE_REPORT - DATE_MURDER
    murder_time_min = random_datetime(
        DATE_MURDER, DATE_MURDER, hour_min=DATE_MURDER.hour - 2, hour_max=DATE_MURDER.hour - 1)
    murder_time_max = random_datetime(
        DATE_MURDER, DATE_MURDER, hour_min=DATE_MURDER.hour + 1, hour_max=DATE_MURDER.hour + 2)
    main_report_path = DATA_DIR / 'main-report.txt'
    main_report = main_report_path.read_text().format(
        days_since_murder=' '.join([
            f'{inflect.number_to_words(days_since_murder.days)}',
            f'{inflect.plural("day", days_since_murder.days)}',
        ]),
        murder_date=f'{DATE_MURDER:%B} {inflect.ordinal(DATE_MURDER.day)}',
        murder_time_min=f'{murder_time_min:%H:%M}',
        murder_time_max=f'{murder_time_max:%H:%M}',
        detective_branch=f'detectives/{MAIN_DETECTIVE.username}',
        access_point=ACCESS_POINT_OF_INTEREST)
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
