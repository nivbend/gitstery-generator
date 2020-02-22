from tempfile import NamedTemporaryFile
from .people import SUSPECTS

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
