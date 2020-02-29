from pathlib import Path
from datetime import timedelta
from click import progressbar
from ..defines import MURDER_DAY, ACCESS_POINT_OF_INTEREST
from ..people import MAIN_DETECTIVE, SUSPECTS
from ..fillers import random_datetimes
from ..git_utils import git_commit, in_branch

@in_branch(f'detectives/{MAIN_DETECTIVE.username}')
def build_phase_2(repo):
    """Second phase requiring some codebase search skills.

    Sometimes we want to search a specific string in the codebase. We can do so using `grep`, `ack`
    and other commands, but git has its own commands to facilitate searches. When we want to link
    a name for certain block of code, for example to answer the question "who wrote this function?",
    we can use `git blame` or `git log -S`.

    To solve the second step, the player will have to match a line in a file to a commit author.
    """
    evidence_dir = Path(repo.working_tree_dir) / 'evidence'
    evidence_dir.mkdir()
    access_log = evidence_dir / 'access.log'

    # We commit each suspect's entry in reverse so that `git log` will lead first to the first
    # suspect's interview on the next step.
    (entry_1, entry_2, entry_3, ) = reversed(SUSPECTS)

    logs = zip(
        [entry_1, entry_2, entry_3, ],
        3 * [ACCESS_POINT_OF_INTEREST, ],
        random_datetimes(3, MURDER_DAY, MURDER_DAY + timedelta(days=1), hour_max=18))
    with progressbar(logs, length=3, label='Comitting factory access logs') as bar:
        for (worker, access_point, time) in bar:
            with access_log.open('a') as l:
                l.write(f'{access_point}\n')
            repo.index.add(access_log.as_posix())
            git_commit(repo, worker, time, f'ACCESS LOG COMMIT {time:%H:%M}')
