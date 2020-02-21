from click import echo, progressbar
from ..defines import DATA_DIR, DATE_START
from ..people import MAYOR, SUSPECTS
from ..fillers import random_paragraphs
from ..git_utils import git_commit, restore_head

def build_phase_3(repo, addresses):
    """Third phase which requires some "big repository" search skills.

    Sometimes we know how to reference a certain commit and would like to see its message or
    contents, like when we want to know why a certain change was made (and hopefully the author is
    responsible enough to describe that in the commit message), or when we want to understand what
    changed along with the code we're currently engaged with (so we'll know what other parts of the
    codebase might require tweaking for the change we have in mind).

    On the other hand, using relative references can at least save us time copying hashes around,
    but can also be useful when using reference ranges (for example to set a commit to rebase on).

    The third step in the mystery will lead to player to both reference a given commit as the N-th
    parent of a known reference, and also display its contents and message using `git show`.
    """
    for (street_name, street_residents) in addresses.items():
        with restore_head(repo):
            # Detach head from current commit. We want only the tag to lead to the "house" commits.
            repo.head.reference = repo.commit('HEAD')
            assert repo.head.is_detached

            # Iterate in reverse so that house number N will be the tag's N-th parent.
            # The `+1` is because we also count the creation of the tag.
            with progressbar(length=len(street_residents) + 1,
                    label=f'Generating street commits: {street_name}') as bar:
                for (i, person) in enumerate(reversed(street_residents)):
                    if person in SUSPECTS:
                        interview_path = DATA_DIR / f'interview-{SUSPECTS.index(person) + 1}.txt'
                        interview = interview_path.read_text()
                    else:
                        interview = random_paragraphs()

                    git_commit(repo, MAYOR, DATE_START,
                        f'{len(street_residents) - i} {street_name}',
                        interview)
                    bar.update(1)

                # Create the tag to the "beginning" of the street.
                git_commit(repo, MAYOR, DATE_START, f'{street_name}')
                street_tag_name = street_name.lower().replace(' ', '_')
                repo.create_tag(f'street/{street_tag_name}')
                bar.update(1)

            for (i, suspect) in enumerate(SUSPECTS):
                if suspect in street_residents:
                    house_number = street_residents.index(suspect) + 1
                    echo(f'  Suspect #{i + 1} lives at #{house_number}')
