class Book:
    ...
    def __lt__(self, other):
        return (self.author, self.title) < (other.author, other.title)