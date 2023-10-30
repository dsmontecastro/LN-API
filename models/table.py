from enum import Enum

class Tables(Enum):
    ALL = { 'symbol': '_', 'title': 'All' }
    CIW = { 'symbol': '✖', 'title': 'Cross Infinite World' }
    JNC = { 'symbol': 'j', 'title': 'J-Novel Club' }
    KOD = { 'symbol': 'K', 'title': 'Kodansha' }
    SEA = { 'symbol': '7', 'title': 'Seven Seas Ent.' }
    YEN = { 'symbol': '¥', 'title': 'Yen Press' }