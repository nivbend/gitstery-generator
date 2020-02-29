from git import Actor
from .utils import rot13

class Person():
    def __init__(self, name, email):
        self.__actor = Actor(name, email)
        self.__address = (None, None)

    @property
    def actor(self):
        return self.__actor

    @property
    def name(self):
        return self.__actor.name

    @property
    def email(self):
        return self.__actor.email

    @property
    def username(self):
        return self.email.split('@')[0]

    @property
    def address(self):
        return self.__address

    def set_address(self, street, number):
        self.__address = (street, number)

    def __lt__(self, other):
        return self.name < other.name

    def __str__(self):
        return f'{self.name} <{self.email}>'

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name!r}>'

MAYOR = Person('Dolores Wholfump', 'mayor@gittown.gov')

MAIN_DETECTIVE = Person('Kyle Pumbinner', 'kpumbinner@gtpd.gittown.gov')
OTHER_DETECTIVES = [
    Person('Angus Wunnard', 'awunnard@gtpd.gittown.gov'),
    Person('Cybil Dopest', 'cdopest@gtpd.gittown.gov'),
    Person('Francine Wronchusher', 'fwronchusher@gtpd.gittown.gov'),
    Person('Aldo Chornoost', 'achornoost@gtpd.gittown.gov'),
    Person('Ira Grazzitch', 'igrazzitch@gtpd.gittown.gov'),
]

# Suspects' names are obfuscated to hide the solution in the source code.
SUSPECTS = [
    Person(rot13('Oebpx Fghvpxneq'), rot13('fghvpxneq.oebpx') + '@commitfactory.com'),
    Person(rot13('Pbfzb Fvjxbax'), rot13('fvjxbax.pbfzb') + '@commitfactory.com'),
    Person(rot13('Ylaqba Uhfxhccre'), rot13('uhfxhccre.ylaqba') + '@commitfactory.com'),
]
