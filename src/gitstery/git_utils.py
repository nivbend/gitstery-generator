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
