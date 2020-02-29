from os import environ, urandom
from itertools import chain
from pathlib import Path
from random import seed
from shutil import rmtree
from click import Path as ClickPath, group, argument, option, confirm, echo, secho
from git import Repo
from .defines import DATA_DIR, DATE_START
from .people import MAYOR
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

    git_commit(repo, MAYOR, DATE_START, 'Git Town')

    secho('Done', fg='green')
