from functools import wraps
from contextlib import contextmanager
from .utils import wrap_paragraphs

def git_commit(repo, author, date, title, body=''):
    # We wrap individual paragraphs in the body, otherwise it'll all get squashed into single
    # wrapped paragraph.
    return repo.index.commit(
        f'{title}\n\n{wrap_paragraphs(body)}' if body else title,
        author=author.actor,
        author_date=date.isoformat(),
        committer=author.actor,
        commit_date=date.isoformat())

@contextmanager
def restore_head(repo):
    prev_head = repo.head.reference
    try:
        yield
    finally:
        prev_head.checkout()

def in_branch(name):
    def _in_branch_decorator(func):
        @wraps(func)
        def _switch_branches(repo, *args, **kwargs):
            with restore_head(repo):
                new_branch = repo.create_head(name)
                new_branch.checkout()
                func(repo, *args, **kwargs)
        return _switch_branches
    return _in_branch_decorator
