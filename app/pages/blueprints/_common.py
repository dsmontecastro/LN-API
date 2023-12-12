from enum import Enum
from json import JSONEncoder
from bson import ObjectId, Decimal128


class MODE(Enum):
    JSON = 'json'
    SHOW = 'show'


class Encoder(JSONEncoder):

    def default(self, o):

        if isinstance(o, ObjectId):
            return str(o)
    
        elif isinstance(o, Decimal128):
            return o.to_decimal()
    
        return JSONEncoder.default(self, o)
