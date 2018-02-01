class Book:
    title = ''
    pages = 0

    def __init__(self, title='', pages=0):
        self.title = title
        self.pages = pages

    def __add__(self, other):
        """Control adding two Books together or a Book and a number"""
        return int(self) + other

    def __radd__(self, other):
        """Control adding a Book and a number w/ the number first"""
        return int(self) + other

    def __int__(self):
        """Return the number of pages"""
        return self.pages

    def __str__(self):
        """Return the Book title"""
        return self.title

    def __lt__(self, other):
        """Return whether this book's page count is less than another number"""
        return self.pages < other

    def __le__(self, other):
        """Return whether this book's page count is less than or
        equal to another Book or a number
        """
        if isinstance(other, Book):
            return self.pages <= other.pages
        elif isinstance(other, (int, float)):
            return self.pages <= other
        else:
            return NotImplemented

    def __eq__(self, other):
        """Return whether this book's page count is equal to another number"""
        return self.pages == other

    def __ne__(self, other):
        """Return whether this book's page count is not equal to another number"""
        return self.pages != other

    def __gt__(self, other):
        """Return whether this book's page count is greater than another number"""
        return self.pages > other

    def __ge__(self, other):
        """Return whether this book's page count is greater than or
        equal to another Book or a number
        """
        if isinstance(other, Book):
            return self.pages >= other.pages
        elif isinstance(other, (int, float)):
            return self.pages >= other
        else:
            return NotImplemented
