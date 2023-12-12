from bson import Decimal128

from ...common.logger import log


class Media(object):

    def __init__(self, format: str, isbn: str, price: str):
        self.format = format.lower()
        self.isbn = isbn.lower()
        self.set_price(price)

    def __str__(self):
        return f"""
            {self.format}
            ISBN: {self.isbn}
            PRICE: {self.price}
        """

    def json(self):
        return {
            'format': self.format,
            'price': self.price,
            'isbn': self.isbn
        }

    def set_price(self, text: str):

        try:

            if text:
                if text[0] == '$': text = text[1:]
                if '.' not in text: text += '.00'
                price = text

            else: price = 'NaN'

            self.price = Decimal128(price)
        
        except:
            self.price = Decimal128('NaN')