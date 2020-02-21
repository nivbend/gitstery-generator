from textwrap import wrap
from click import echo
from ..defines import DATA_DIR, DATE_REPORT, POLICE_BRANCH
from ..people import MAIN_DETECTIVE
from ..fillers import random_ids
from ..git_utils import git_commit, in_branch

@in_branch(POLICE_BRANCH)
def build_phase_1(repo):
    """First phase requiring some history lookup skills."""
    report_ids = random_ids()

    echo('Committing the main crime scene report')
    main_report_path = DATA_DIR / 'main-report.txt'
    main_report = main_report_path.read_text()
    git_commit(repo, MAIN_DETECTIVE, DATE_REPORT,
        f'Crime scene report #{next(report_ids)}',
        '\n\n'.join('\n'.join(wrap(paragraph)) for paragraph in main_report.split('\n\n')))
