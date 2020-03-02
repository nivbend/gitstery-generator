import sys
from os import environ, urandom
from urllib.parse import urlparse
from itertools import chain
from pathlib import Path
from contextlib import contextmanager, nullcontext
from datetime import timedelta
from random import seed, choice, choices, randrange
from shutil import rmtree
from tempfile import TemporaryDirectory
from csv import DictWriter
from inflect import engine
from click import (Path as ClickPath, group, pass_context, argument, option, prompt, confirm, echo,
    secho, IntRange)
from git import Repo
from .defines import DATA_DIR, DATE_START, DATE_REPORT_WEEK_START, POLICE_BRANCH
from .people import MAYOR, MAIN_DETECTIVE, OTHER_DETECTIVES, SUSPECTS, FACTORY_WORKERS
from .fillers import random_people
from .git_utils import git_commit
from .phases import PHASES_COUNT, build_phase_1, build_phase_2, build_phase_3
from .solution import build_solution, verify_repository

@contextmanager
def clone_repository(url):
    with TemporaryDirectory() as temporary_directory:
        echo(f'Cloning {url} to {temporary_directory}')
        cloned = Repo.clone_from(url, temporary_directory)
        yield cloned

@group()
def cli():
    # Clear all git environment variables to avoid them interacting with commands.
    # For exmaple, `generate` during a git rebase will re-initialize the current repository
    # because of the `GIT_DIR` environment variable.
    for env_var in environ:
        if env_var.startswith('GIT_'):
            del environ[env_var]

@cli.command()
@argument('repo_dir', type=ClickPath(file_okay=False, writable=True), envvar='GITSTERY_TEMP_DIR')
@option('--force', '-f', is_flag=True, help='Override directory even if exists.')
@option('--seed', '-s', 'seed_value', type=bytes.fromhex, metavar='SEED', envvar='GITSTERY_SEED',
    help='Set random seed for reproducible runs.')
@option('--phase', '-p', 'chosen_phases', type=IntRange(1, PHASES_COUNT), default=[], show_default=f'1..{PHASES_COUNT}',
        metavar='INDEX', multiple=True, help='Generate only selected phases.')
@option('--no-phases', '-P', is_flag=True, show_default=True, help="Don't generate any phases.")
@option('--no-solution', '-S', is_flag=True, show_default=True, help="Don't generate solution.")
@option('--push', 'push_remote', is_flag=True, show_default=True, help='Push to target repository.')
@option('--target-repository', '--target-repo', '--target', '-t', 'remote_url', metavar='URL',
    envvar='GITSTERY_TARGET_REPO', help='Target repository.')
@pass_context
def generate(ctx, repo_dir, force, seed_value, chosen_phases, no_phases, no_solution, push_remote,
        remote_url):
    """Generate a git repository of a Git Murder Mystery."""
    seed_value = seed_value if seed_value else urandom(10)
    echo(f'Using seed {seed_value.hex()}')
    seed(seed_value)

    everyone = list(sorted(chain(
        [MAYOR, MAIN_DETECTIVE, ],
        OTHER_DETECTIVES,
        SUSPECTS,
        FACTORY_WORKERS)))

    addresses = {
        'Badgers Dene': randrange(40, 200) * [None, ],
        'Balcombe Close': randrange(40, 200) * [None, ],
        'Beaconside': randrange(40, 200) * [None, ],
        'Bowler Street': randrange(40, 200) * [None, ],
        'Cliff Place': randrange(40, 200) * [None, ],
        'Corbet Close': randrange(40, 200) * [None, ],
        'Down Close': randrange(40, 200) * [None, ],
        'Glan Road': randrange(40, 200) * [None, ],
        'Glendale': randrange(40, 200) * [None, ],
        'Harvey Street': randrange(40, 200) * [None, ],
        'Holmefield Avenue': randrange(40, 200) * [None, ],
        'Larch Walk': randrange(40, 200) * [None, ],
        'Moor End': randrange(40, 200) * [None, ],
        'Sunningdale Drive': randrange(40, 200) * [None, ],
        'Tamworth Drive': randrange(40, 200) * [None, ],
        'Valentia Road': randrange(40, 200) * [None, ],
        'Ventnor Terrace': randrange(40, 200) * [None, ],
        'Wantage Close': randrange(40, 200) * [None, ],
        'Wellswood Gardens': randrange(40, 200) * [None, ],
        'Wilson Gardens': randrange(40, 200) * [None, ],
    }

    # Assign "notable" people random addresses. Notice that the street number isn't zero-based.
    street_assignments = choices(list(addresses.keys()), k=len(everyone))
    for (person, street_name) in zip(everyone, street_assignments):
        street_number = choice([i + 1 for (i, p) in enumerate(addresses[street_name]) if p is None])
        person.set_address(street_name, street_number)
        addresses[street_name][street_number - 1] = person

    # Fill in remaining addresses with random people.
    for (street_name, street_residents) in addresses.items():
        for (i, person) in zip(range(len(street_residents)), random_people(everyone)):
            if street_residents[i]:
                continue
            street_residents[i] = person
            person.set_address(street_name, street_number)

    repo_dir = Path(repo_dir)
    if repo_dir.exists():
        if not force and any(repo_dir.iterdir()):
            confirm(f"Directory {repo_dir} isn't empty, you sure you want to override it?",
                abort=True)
        rmtree(repo_dir)

    secho('Initialization', fg='magenta')
    echo('Creating repository')
    repo = Repo.init(repo_dir, mkdir=True)
    repo.description = f'A Git Murder Mystery ({seed_value.hex()})'
    repo_root = Path(repo.working_tree_dir)

    inflect = engine()
    readme = DATA_DIR.joinpath('README.md').read_text()
    repo_root.joinpath('README.md').write_text(readme)
    reference_date = DATE_REPORT_WEEK_START - timedelta(days=2)
    instructions = DATA_DIR.joinpath('instructions.txt').read_text().format(
        detective=MAIN_DETECTIVE.name,
        police_branch=POLICE_BRANCH,
        reference_date=f'{reference_date:%A, %B} {inflect.ordinal(reference_date.day)}')
    repo_root.joinpath('instructions.txt').write_text(instructions)

    repo.index.add(
        p.as_posix() for p in repo_root.glob('**/*')
        if p.is_file() and '.git' not in p.parts)

    echo('Writing residents file')
    residents = repo_root / 'residents.txt'
    with residents.open('w') as residents_csv:
        writer = DictWriter(
            residents_csv,
            fieldnames=('Name', 'Address', ),
            dialect='excel-tab',
            lineterminator='\n')
        writer.writeheader()
        for person in sorted(chain(*addresses.values())):
            writer.writerow({
                'Name': person.name,
                'Address': f'{person.address[1]} {person.address[0]}',
            })
    repo.index.add(residents.as_posix())

    git_commit(repo, MAYOR, DATE_START, 'Git Town')

    if not no_phases:
        phases = (
            lambda: build_phase_1(repo),
            lambda: build_phase_2(repo),
            lambda: build_phase_3(repo, addresses),
        )
        chosen_phases = set(chosen_phases) if chosen_phases else range(1, len(phases) + 1)
        for (i, phase) in enumerate(phases):
            if i + 1 not in chosen_phases:
                secho(f'Skipping phase #{i + 1}', fg='cyan')
                continue
            secho(f'Phase #{i + 1}', fg='magenta')
            phase()

    if not no_solution:
        secho('Encoding the solution', fg='magenta')
        build_solution(repo, addresses)

    if push_remote:
        while not remote_url:
            remote_url = prompt('Target repository').strip()
        ctx.invoke(push, repo=repo, url=remote_url)

    secho('Done', fg='green')

@cli.command()
@argument('repo', type=Repo, envvar='GITSTERY_TEMP_DIR')
@argument('url', envvar='GITSTERY_TARGET_REPO')
def push(repo, url):
    """Update the remote repository at URL from the mystery repository at REPO."""
    if 'origin' in repo.remotes:
        repo.delete_remote('origin')
    origin = repo.create_remote('origin', url)

    try:
        secho(f'Pushing {repo.working_tree_dir} to {url}', fg='magenta')
        pushed_refs = origin.push(repo.branches, force=True, tags=True)
        for ref in pushed_refs:
            summary = ref.summary.strip('\n')
            echo(f'  {ref.local_ref} {summary}')
    finally:
        repo.delete_remote('origin')

@cli.command()
@argument('repository', envvar='GITSTERY_TARGET_REPO')
def verify(repository):
    """Verify a mystery REPOSITORY was built properly."""
    uri = urlparse(repository)
    if uri.scheme.lower() in ('http', 'https') or uri.path.startswith('git@'):
        repo_context = clone_repository(repository)
    else:
        try:
            # This also takes care of `file://` URIs.
            repo_context = nullcontext(Repo(uri.path))
        except:
            echo(f'{repository}: Not a git repository')
            sys.exit(1)

    with repo_context as repo:
        if 'master' != repo.head.ref.name:
            echo('Checking out `master`')
            repo.heads.master.checkout()

        if repo.head.is_detached:
            echo("Repository's head is detached")
            sys.exit(1)
        if repo.is_dirty():
            echo('Repository is dirty')
            sys.exit(1)

        if not verify_repository(repo):
            sys.exit(1)
