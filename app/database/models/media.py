class Media(object):

    def __init__(self, format: str, isbn: str, price: str):
        self.format = format.lower()
        self.isbn = isbn.lower()
        self.price = price

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