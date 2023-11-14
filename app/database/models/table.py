from enum import Enum

class Table():
    def __init__(self, symbol: str, title: str):
        self.symbol: str = symbol
        self.title: str = title


class Tables(Enum):
    ERR = Table('', '')
    ALL = Table('_', 'All Tables')
    CIW = Table('✖', 'Cross Infinite World')
    JNC = Table('j', 'J-Novel Club')
    KOD = Table('K', 'Kodansha')
    SEA = Table('7', 'Seven Seas Ent.')
    YEN = Table('¥', 'Yen Press')