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

# Factory workers' names are obfuscated same as the suspects'.
FACTORY_WORKERS = [
    Person(rot13('Oehab Cebvmmna'), rot13('cebvmmna.oehab') + '@commitfactory.com'),
    Person(rot13('Ryiven Cbzznff'), rot13('cbzznff.ryiven') + '@commitfactory.com'),
    Person(rot13('Senapvar Jbeehccre'), rot13('jbeehccre.senapvar') + '@commitfactory.com'),
    Person(rot13('Virf Cevagvqqyr'), rot13('cevagvqqyr.virf') + '@commitfactory.com'),
    Person(rot13('Xriva Urgubex'), rot13('urgubex.xriva') + '@commitfactory.com'),
    Person(rot13('Xvatfyrl Pbgbyq'), rot13('pbgbyq.xvatfyrl') + '@commitfactory.com'),
    Person(rot13('Fgreyvat Oenzzre'), rot13('oenzzre.fgreyvat') + '@commitfactory.com'),
    Person(rot13('Flovy Tybec'), rot13('tybec.flovy') + '@commitfactory.com'),
]
