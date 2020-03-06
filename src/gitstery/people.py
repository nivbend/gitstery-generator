from git import Actor

class Person():
    def __init__(self, name, email):
        self.__actor = Actor(name, email)

    @property
    def actor(self):
        return self.__actor

    @property
    def name(self):
        return self.__actor.name

    @property
    def email(self):
        return self.__actor.email

    def __lt__(self, other):
        return self.name < other.name

    def __str__(self):
        return f'{self.name} <{self.email}>'

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name!r}>'

MAYOR = Person('Dolores Wholfump', 'mayor@gittown.gov')
