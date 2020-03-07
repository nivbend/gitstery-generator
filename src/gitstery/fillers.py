from itertools import islice
from datetime import timedelta
from random import choice, randrange
from textwrap import dedent
from .defines import DATA_DIR, DATE_START
from .people import Person

def random_ids():
    past = set()
    while True:
        n = randrange(10000, 999999)
        if n not in past:
            yield n
            past.add(n)

def random_people(people_of_interest):
    providers = ['gitgle.com', 'rebase.org', 'committers.org', 'thegit.com', ]
    given_names_path = DATA_DIR / 'given-names.txt'
    surnames_path = DATA_DIR / 'surnames.txt'
    given_names = given_names_path.read_text().splitlines()
    surnames = surnames_path.read_text().splitlines()
    people = {tuple(p.name.split()) for p in people_of_interest}
    while True:
        given_name = choice(given_names)
        surname = choice(surnames)
        if (given_name, surname) in people:
            continue

        email = f'{given_name[0].lower()}{surname.lower()}@{choice(providers)}'
        yield Person(f'{given_name} {surname}', email)
        people.add((given_name, surname))

def random_paragraphs(count = -1):
    global _paragraphs
    if not _paragraphs:
        # Load book for random paragraphs.
        book_path = DATA_DIR / 'book.txt'
        with book_path.open('r') as book:
            # Split the book by paragraphs, we drop the first 50 "paragraphs" to skip the title, TOC,
            # and parts of the exposition. We also drop "empty" paragraph, stories and chapter titles.
            # No need to wrap the paragraph right now, `git_commit` takes care of that.
            _paragraphs = (' '.join(dedent(p).splitlines()) for p in book.read().split('\n\n'))
            _paragraphs = [p for p in islice(_paragraphs, 50, None)
                if p and not (p.startswith(' ') or p.startswith('CHAPTER'))]

    if count is None:
        return choice(_paragraphs)
    if count <= 0:
        count = 2 + randrange(5)
    index = randrange(len(_paragraphs))
    return '\n\n'.join(_paragraphs[index:index + count])

_paragraphs = None

def random_datetime(date_1, date_2=None, /, *, hour_min=8, hour_max=18):
    (start, end) = (date_1, date_2) if date_2 else (DATE_START, date_1)
    delta = end - start
    return start.replace(hour=0, minute=0) + timedelta(
        days=randrange(delta.days) if 0 < delta.days else 0,
        hours=randrange(hour_min, hour_max),
        minutes=randrange(0, 59))

def random_datetimes(count, date_1, date_2 = None, /, *, hour_min=8, hour_max=18):
    (start, end) = (date_1, date_2) if date_2 else (DATE_START, date_1)
    return sorted(random_datetime(start, end, hour_min=hour_min, hour_max=hour_max)
        for _ in range(count))
