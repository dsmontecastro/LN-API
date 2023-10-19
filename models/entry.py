from datetime import datetime, date as Date

class Media(object):

    def __init__(self, format: str, isbn: str, price: str):
        self.isbn = isbn
        self.price = price
        self.format = format

    def __str__(self):
        return f"""
            {self.format}
            ISBN: {self.isbn}
            PRICE: {self.price}
        """

class Entry(object):

    def __init__(self,
        url = '',
        date = '',
        title = '',
        cover = '',
        blurb = '',
        genres: list[str] = [],
        credits: list[str] = [],
        media: list[Media] = [],
    ):

        # Raw Strings
        self.url: str = url
        self.title: str = title
        self.cover: str = cover
        self.blurb: str = blurb

        # List of Strings
        self.genres: list[str] = genres
        self.credits: list[str] = credits
        self.media: list[Media] = media
    
        # Requires processing
        self.date: Date = datetime.strptime(date, '%m/%d/%y').date()

    def __str__(self):
        return f"""
            @{self.date.strftime('%m-%d-$y')}
            url = {self.url}
            title = {self.title}
            cover = {self.cover}
            blurb = {self.blurb}
            genres = {self.genres}
            credits = {self.credits}
            media = {self.media.__str__()}
        """
