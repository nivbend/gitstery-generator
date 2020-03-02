import re
from datetime import datetime
from subprocess import check_output
from pathlib import Path
from tempfile import NamedTemporaryFile
from click import echo, secho
from .defines import (DATE_REPORT, DATE_REPORT_WEEK_START, DATE_REPORT_WEEK_END, POLICE_BRANCH,
    ACCESS_POINT_OF_INTEREST)
from .people import MAIN_DETECTIVE, SUSPECTS
from .utils import rot13

def build_solution(repo, addresses):
    # First we generate a hash for the solution to store as the contents of the `solution` tag.
    # We append a newline to the murderer's name because the check will use `echo` that appends it
    # as well. We don't actually write the object so its contents won't appear in the repository.
    # The index to the real murderer is obfuscated to not give it away in the source code :)
    murderer = SUSPECTS[sum(int(t, int(str(sum(len(t) for t in addresses) // 10 - 1), 16)) for t in map(''.join, zip('zip', 'join'))) & ord('T') % ord('-') % ord('$')]
    with NamedTemporaryFile('w') as solution:
        solution.write(murderer.name + '\n')
        solution.flush()
        solution_hash = repo.git.hash_object(solution.name)

    # We encode the solution as a new data object and tag it. That way it won't appear in the
    # repository's filesystem or git log, but can still be addressable.
    with NamedTemporaryFile('w') as solution:
        solution.write(solution_hash)
        solution.flush()
        solution_ref = repo.git.hash_object('-w', solution.name)

    repo.create_tag('solution', ref=solution_ref)

def verify_repository(repo):
    ###  NOTE - SPOILER ALERT!!!!
    # This function is used to verify the repository generated during development. If you haven't
    # solved the mystery yet, don't spoil the way to the solution for yourself by reading it.
    repo_root = Path(repo.working_tree_dir)
    try:
        (police_branch, ) = (branch for branch in repo.refs if branch.name.endswith(POLICE_BRANCH))
    except ValueError as err:
        echo(f'Missing police archive branch: {err}')
        return False

    try:
        (detective_branch, ) = (branch for branch in repo.refs
            if branch.name.endswith(f'detectives/{MAIN_DETECTIVE.username}'))
    except ValueError as err:
        echo(f"Missing main detective's branch: {err}")
        return False

    if not repo_root.joinpath('README.md').exists():
        echo("Can't find 'README.md'")
        return False
    instructions = repo_root / 'instructions.txt'
    if not instructions.exists():
        echo(f"Can't find '{instructions.name}'")
        return False
    instructions_text = instructions.read_text()
    if MAIN_DETECTIVE.name not in instructions_text:
        echo(f"The main detective's name ({MAIN_DETECTIVE.name}) isn't in '{instructions.name}'")
        return False
    elif POLICE_BRANCH not in instructions_text:
        echo(f"The policy branch name ({POLICE_BRANCH}) isn't in '{instructions.name}'")
        return False

    secho('Finding main report commit', fg='magenta')
    regex_commit_log = re.compile('\n'.join([
        r'commit [0-9a-f]+',
        r'Author: +(.+) <.+>',
        r'Date: +(.+)',
        r'',
        r'(.*)(?:\n((?: +.*\n*)+))?',
    ]), re.MULTILINE)
    commits = regex_commit_log.findall(repo.git.log(
        '--since', f'{DATE_REPORT_WEEK_START:%d/%m/%Y}',
        '--before', f'{DATE_REPORT_WEEK_END:%d/%m/%Y}',
        '--author', f'{MAIN_DETECTIVE.name}',
        police_branch))
    if not commits:
        echo('No commits match for main report')
        return False
    elif 1 < len(commits):
        echo(f'Multiple commits ({len(commits)}) match main report')
        return False
    ((author, timestamp, title, main_report, ), ) = commits
    timestamp = datetime.strptime(timestamp, '%a %b %d %H:%M:%S %Y %z').replace(tzinfo=None)
    assert MAIN_DETECTIVE.name == author
    assert 'Crime scene report' in title
    assert DATE_REPORT == timestamp
    assert ACCESS_POINT_OF_INTEREST in main_report
    assert f'detectives/{MAIN_DETECTIVE.username}' in main_report

    secho('Finding suspects in access log', fg='magenta')
    commits = regex_commit_log.findall(repo.git.log(
        f'-S{ACCESS_POINT_OF_INTEREST}',
        detective_branch))
    if not len(SUSPECTS) == len(commits):
        echo(f'Expected number {len(SUSPECTS)} commits, got {len(commits)}')
        return False
    suspect_names = set(author for (author, _, _, _) in commits)
    current_suspects = set(s.name for s in SUSPECTS)
    assert current_suspects == suspect_names

    secho("Finding suspects' addresses", fg='magenta')
    addresses = []
    regex_address = re.compile('^residents.txt:.+\t([0-9]+) (.+)$')
    for suspect_name in suspect_names:
        match = regex_address.match(repo.git.grep('-w', suspect_name, '--', 'residents.txt'))
        if not match:
            echo(f"Failed to find {suspect_name}'s address")
            return False
        (number, street_name, ) = match.groups()
        addresses.append((suspect_name, street_name, int(number)))

    secho('Interviewing suspects', fg='magenta')
    lead = rot13('terra Ulhaqnv')
    for (suspect_name, street_name, number) in addresses:
        street_tag_name = street_name.lower().replace(' ', '_')
        street_ref = f'street/{street_tag_name}~{number}'
        (_, _, _, commit_msg) = regex_commit_log.match(repo.git.show('-s', street_ref)).groups()
        if lead in commit_msg:
            echo('  Got a lead by interviewing a suspect')
            current_suspects.remove(suspect_name)
            continue
        investigate_ref = repo.git.show(f'{street_ref}:investigate')
        investigation = repo.git.show(investigate_ref)
        if lead not in investigation:
            echo('  Suspect dropped due to lead')
            current_suspects.remove(suspect_name)

    try:
        (suspect, ) = current_suspects
    except ValueError:
        echo(f"Couldn't reduce number of suspects ({len(current_suspects)})")
        return False

    secho('Checking suspect', fg='magenta')
    solution_hash = check_output(
        f'echo "{suspect}" | git hash-object --stdin',
        cwd=repo_root,
        shell=True,
        universal_newlines=True)
    if solution_hash.strip('\n') != repo.git.show('solution'):
        echo('Found the wrong suspect!')
        return False

    secho('Good!', fg='green')
    return True
