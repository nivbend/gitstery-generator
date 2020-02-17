from os import environ, urandom
from itertools import chain
from pathlib import Path
from random import seed, choice, choices, randrange
from shutil import rmtree
from csv import DictWriter
from click import Path as ClickPath, group, argument, option, confirm, echo, secho
from git import Repo
from .defines import DATA_DIR, DATE_START
from .people import MAYOR
from .fillers import random_people
from .git_utils import git_commit

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
def generate(repo_dir, force, seed_value):
    """Generate a git repository of a Git Murder Mystery."""
    seed_value = seed_value if seed_value else urandom(10)
    echo(f'Using seed {seed_value.hex()}')
    seed(seed_value)

    everyone = list(sorted(chain(
        [MAYOR, ])))

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

    readme = DATA_DIR.joinpath('README.md').read_text()
    repo_root.joinpath('README.md').write_text(readme)
    instructions = DATA_DIR.joinpath('instructions.txt').read_text()
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

    secho('Done', fg='green')