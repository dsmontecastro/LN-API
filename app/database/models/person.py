class Person(object):

    def __init__(self, name: str, position: str):
        self.name = name
        self.position = position

    def __str__(self):
        return f'{self.position}: {self.name}'

    def json(self):
        return {
            'name': self.name,
            'position': self.position
        }