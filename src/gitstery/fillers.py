from random import choice
from .defines import DATA_DIR
from .people import Person

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
