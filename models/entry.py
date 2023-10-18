from datetime import datetime, date as Date

class Entry(object):

    def __init__(self, url = '', date = '', isbn = '', title = '', image = '', blurb = '', medium = '', genres = ['']):

        # Uses raw strings
        self.url: str = url
        self.isbn: str = isbn
        self.title: str = title
        self.image: str = image
        self.blurb: str = blurb
        self.medium: str = medium
        self.genres: list[str] = genres

        # Requires processing
        self.date: Date = datetime.strptime(date, '%m/%d/%y').date()

    def __str__(self):
        return f"""
            url = {self.url}
            date = {self.date}
            isbn = {self.isbn}
            title = {self.title}
            medium = {self.medium}
            genres = {self.genres}
        """
